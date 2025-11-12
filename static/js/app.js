// Chart instances
let animalChart, timeChart, distanceChart;
let allFeeds = []; // Store all feeds for interaction

// Configuration
const CONFIG = {
    refreshInterval: 30000, // 30 seconds
    animalIcons: {
        "Fox": "fa-fox", "Badger": "fa-otter", "Deer": "fa-deer",
        "Squirrel": "fa-squirrel", "Rabbit": "fa-rabbit", "Hedgehog": "fa-hedgehog",
        "Owl": "fa-owl", "Woodpecker": "fa-crow", "Boar": "fa-boar",
        "Bear": "fa-bear-paw", "Raccoon": "fa-raccoon", "Skunk": "fa-skunk",
        "Lynx": "fa-cat", "Wolf": "fa-wolf-pack", "Moose": "fa-moose",
        "Unknown": "fa-question-circle"
    },
    animalColors: [
        '#4caf50', '#8bc34a', '#cddc39', '#ffeb3b', '#ffc107', '#ff9800',
        '#ff5722', '#e91e63', '#9c27b0', '#673ab7', '#3f51b5', '#2196f3',
        '#00bcd4', '#009688', '#795548'
    ]
};

// Chart.js Global Defaults
Chart.defaults.color = '#c8ccc8';
Chart.defaults.borderColor = 'rgba(255, 255, 255, 0.1)';
Chart.defaults.font.family = "'Inter', sans-serif";

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    console.log('Forest Watch Dashboard Initialized');
    initializeCharts();
    fetchDashboardData();
    setInterval(fetchDashboardData, CONFIG.refreshInterval);
    document.getElementById('timelineContainer').addEventListener('click', handleTimelineClick);
});

/**
 * Fetch all data from the new single backend endpoint
 */
async function fetchDashboardData() {
    try {
        const response = await fetch('/api/dashboard');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();

        if (data.error) {
            updateStatus('error', 'Connection Error');
            return;
        }
        
        allFeeds = data.timeline || [];
        
        updateStatus('connected', allFeeds.length > 0 ? 'Live' : 'Awaiting Data');
        updateDashboard(data);
        
    } catch (error) {
        updateStatus('error', 'Connection Error');
        console.error('Error loading dashboard data:', error);
    }
}

/**
 * Update all components of the dashboard with data from the backend
 */
function updateDashboard(data) {
    updateStats(data.stats);
    updateCharts(data.charts);
    updateTimeline(data.timeline);

    const latestSighting = data.timeline.find(f => f.motion === 1);
    if (latestSighting) {
        updateSelectedSighting(latestSighting.entry_id);
    } else {
        clearSelectedSighting();
    }
}

/**
 * Initialize all Chart.js charts
 */
function initializeCharts() {
    const pieOptions = {
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { position: 'bottom', labels: { padding: 15, font: { size: 12 } } } }
    };
    animalChart = new Chart(document.getElementById('animalChart'), {
        type: 'pie', data: { labels: [], datasets: [{ data: [], backgroundColor: CONFIG.animalColors }] }, options: pieOptions
    });
    timeChart = new Chart(document.getElementById('timeChart'), {
        type: 'doughnut', data: { labels: [], datasets: [{ data: [], backgroundColor: ['#2d4a23', '#8c6b5d', '#a5d6a7'] }] }, options: pieOptions
    });
    distanceChart = new Chart(document.getElementById('distanceChart'), {
        type: 'line',
        data: { labels: [], datasets: [{
            label: 'Proximity (m)', data: [], borderColor: '#a5d6a7', backgroundColor: 'rgba(165, 214, 167, 0.2)',
            borderWidth: 2, fill: true, tension: 0.4, pointRadius: 3, pointBackgroundColor: '#a5d6a7'
        }]},
        options: {
            responsive: true, maintainAspectRatio: false,
            scales: {
                y: { beginAtZero: true, title: { display: true, text: 'Proximity (m)' } },
                x: { type: 'time', time: { unit: 'hour' }, title: { display: true, text: 'Time' } }
            }
        }
    });
}

/**
 * Update statistics cards
 */
function updateStats(stats) {
    if (!stats) return;
    document.getElementById('totalDetections').textContent = stats.total_detections || 0;
    document.getElementById('validDetections').textContent = stats.valid_detections || 0;
    document.getElementById('avgDistance').textContent = `${(stats.average_distance / 100).toFixed(1)} m` || '0 m';
    document.getElementById('animalTypes').textContent = stats.animal_types || 0;
}

/**
 * Update all charts with new data
 */
function updateCharts(charts) {
    if (!charts) return;
    
    // Update Animal Distribution Chart
    animalChart.data.labels = charts.animal_distribution.labels;
    animalChart.data.datasets[0].data = charts.animal_distribution.data;
    animalChart.update('none');
    
    // Update Time of Day Chart
    timeChart.data.labels = charts.time_distribution.labels;
    timeChart.data.datasets[0].data = charts.time_distribution.data;
    timeChart.update('none');
    
    // Update Distance Chart
    distanceChart.data.datasets[0].data = charts.proximity_over_time;
    distanceChart.update('none');
}

/**
 * Update the timeline with recent sightings
 */
function updateTimeline(timeline) {
    const container = document.getElementById('timelineContainer');
    const sightingFeeds = timeline.filter(f => f.motion === 1).reverse();
    
    if (sightingFeeds.length === 0) {
        container.innerHTML = '<div class="loading-placeholder">Awaiting sensor data...</div>';
        return;
    }
    container.innerHTML = sightingFeeds.map(createTimelineItem).join('');
}

/**
 * Create HTML for a single timeline item
 */
function createTimelineItem(feed) {
    const { is_valid_detection, false_positive, animal_type, distance, time_of_day, timestamp, entry_id } = feed;
    
    let statusClass = 'no-motion', icon = 'fa-question-circle', title = 'Motion Detected';

    if (false_positive) {
        statusClass = 'false-positive';
        icon = 'fa-exclamation-triangle';
        title = 'False Positive';
    } else if (is_valid_detection) {
        statusClass = 'valid';
        icon = CONFIG.animalIcons[animal_type] || 'fa-paw';
        title = animal_type;
    }
    
    return `
        <div class="timeline-item ${statusClass}" data-entry-id="${entry_id}">
            <div class="timeline-icon"><i class="fas ${icon}"></i></div>
            <div class="timeline-content">
                <h4>${title}</h4>
                <p>${(distance / 100).toFixed(1)}m | ${time_of_day}</p>
            </div>
            <div class="timeline-time">${formatTimestamp(timestamp)}</div>
        </div>
    `;
}

/**
 * Handle clicks on the timeline
 */
function handleTimelineClick(event) {
    const item = event.target.closest('.timeline-item');
    if (item && item.dataset.entryId) {
        updateSelectedSighting(parseInt(item.dataset.entryId));
    }
}

/**
 * Update the "Selected Sighting" card
 */
function updateSelectedSighting(entryId) {
    const feed = allFeeds.find(f => f.entry_id === entryId);
    if (!feed) return;

    // Update active state in timeline
    document.querySelectorAll('.timeline-item').forEach(el => {
        el.classList.toggle('active', parseInt(el.dataset.entryId) === entryId);
    });

    const { animal_type, distance, time_of_day, timestamp, false_positive, is_valid_detection } = feed;

    let status = 'Unknown', statusClass = 'unknown';
    if (false_positive) {
        status = 'False Positive';
        statusClass = 'false-positive';
    } else if (is_valid_detection) {
        status = 'Confirmed';
        statusClass = 'confirmed';
    }

    document.getElementById('selectedTimestamp').textContent = formatTimestamp(timestamp);
    document.getElementById('selectedAnimalIcon').innerHTML = `<i class="fas ${CONFIG.animalIcons[animal_type] || 'fa-question'}"></i>`;
    document.getElementById('selectedAnimalName').textContent = animal_type;
    document.getElementById('selectedDistance').textContent = `${(distance / 100).toFixed(1)} m`;
    document.getElementById('selectedTimeOfDay').textContent = time_of_day;
    
    const statusEl = document.getElementById('selectedStatus');
    statusEl.textContent = status;
    statusEl.className = `status-badge ${statusClass}`;
}

function clearSelectedSighting() {
    document.getElementById('selectedTimestamp').textContent = '--';
    document.getElementById('selectedAnimalIcon').innerHTML = `<i class="fas fa-question"></i>`;
    document.getElementById('selectedAnimalName').textContent = 'Awaiting Data';
    document.getElementById('selectedDistance').textContent = '--';
    document.getElementById('selectedTimeOfDay').textContent = '--';
    const statusEl = document.getElementById('selectedStatus');
    statusEl.textContent = '--';
    statusEl.className = 'status-badge';
}

/**
 * Update connection status indicator
 */
function updateStatus(status, text) {
    const dot = document.querySelector('#statusIndicator .status-dot');
    const textEl = document.getElementById('statusText');
    if(dot) dot.className = 'status-dot ' + status;
    if(textEl) textEl.textContent = text;
}

/**
 * Format timestamp for display
 */
function formatTimestamp(timestamp, short = false) {
    if (!timestamp) return '--';
    const date = new Date(timestamp);
    if (isNaN(date.getTime())) return timestamp;
    
    if (short) return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });

    const now = new Date();
    const diffMins = Math.round((now - date) / 60000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} min ago`;
    if (diffMins < 1440) return `${Math.round(diffMins/60)}h ago`;
    
    return date.toLocaleDateString();
}