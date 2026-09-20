from app import app
from models import MFAConfiguration, LoginAttempt, User, db
from utils.security import hash_password
import pyotp


def run_checks():
    with app.app_context():
        db.drop_all()
        db.create_all()

        user = User(
            username='demo',
            email='demo@example.com',
            password_hash=hash_password('Demo@123'),
            mfa_secret=pyotp.random_base32(),
        )
        db.session.add(user)
        db.session.commit()

        db.session.add(MFAConfiguration(user_id=user.id, secret=user.mfa_secret, enabled=False))
        db.session.commit()

        client = app.test_client()

        # Normal login
        response = client.post('/login', data={'username': 'demo', 'password': 'Demo@123', 'demo_mode': 'normal'})
        print('LOW_STATUS', response.status_code, response.headers.get('Location'))
        assert response.status_code in (200, 302)

        # Medium-risk MFA challenge
        response = client.post('/login', data={'username': 'demo', 'password': 'Demo@123', 'demo_mode': 'medium'})
        print('MEDIUM_STATUS', response.status_code, response.headers.get('Location'))
        assert response.status_code in (200, 302)
        secret = MFAConfiguration.query.filter_by(user_id=user.id).first().secret
        otp = pyotp.TOTP(secret).now()
        response = client.post('/mfa', data={'otp': otp})
        print('MFA_RESULT', response.status_code, response.headers.get('Location'))
        assert response.status_code in (200, 302)

        # High-risk blocked login
        response = client.post('/login', data={'username': 'demo', 'password': 'Demo@123', 'demo_mode': 'high'})
        print('HIGH_STATUS', response.status_code)
        assert response.status_code == 200
        body = response.get_data(as_text=True)
        assert 'HIGH' in body or 'blocked' in body.lower()

        attempts = LoginAttempt.query.order_by(LoginAttempt.timestamp.desc()).all()
        print('ATTEMPT_OUTCOMES', [a.outcome for a in attempts])
        print('TOTAL_ATTEMPTS', len(attempts))
        assert any(a.outcome == 'success' for a in attempts)


if __name__ == '__main__':
    run_checks()
