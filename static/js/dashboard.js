document.addEventListener('DOMContentLoaded', () => {
    const riskChart = document.getElementById('riskChart');
    if (riskChart) {
        const scores = JSON.parse(riskChart.dataset.riskScores || '[]');
        if (scores.length > 0) {
            const max = Math.max(...scores, 100);
            riskChart.innerHTML = '';
            scores.slice().reverse().forEach((score) => {
                const bar = document.createElement('div');
                bar.className = 'chart-bar';
                bar.dataset.value = String(score);
                const heightPct = Math.max((score / max) * 100, 10);
                bar.style.height = `${heightPct}%`;
                riskChart.appendChild(bar);
            });
        }
    }

    const activityChart = document.getElementById('activityChart');
    if (activityChart) {
        const activity = JSON.parse(activityChart.dataset.activity || '[]');
        if (activity.length > 0) {
            activityChart.innerHTML = '';
            activity.slice().reverse().forEach((item) => {
                const cell = document.createElement('div');
                cell.className = 'activity-cell';
                const bar = document.createElement('div');
                bar.className = 'activity-bar';
                bar.style.height = `${Math.max(item.value * 100, 18)}%`;
                const label = document.createElement('span');
                label.className = 'activity-label';
                label.textContent = item.label || 'L';
                cell.appendChild(bar);
                cell.appendChild(label);
                activityChart.appendChild(cell);
            });
        }
    }
});
