// Chart instances
let animalChart = null;
let timeChart = null;
let distanceChart = null;

// Configuration
const CONFIG = {
    refreshInterval: 30000, // 30 seconds
    maxTimelineItems: 15
};

// Chart.js Global Defaults
Chart.defaults.color = '#c8ccc8';
Chart.defaults.borderColor = 'rgba(255, 255, 255, 0.1)';
Chart.defaults.font.family = "'Inter', sans-serif";

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    console.log('Forest Watch Dashboard Initialized');
    initializeCharts();
    loadData();
    loadStats();
    loadLatest();
    
    // Set up auto-refresh
    setInterval(() => {
        loadData();
        loadStats();
        loadLatest();
    }, CONFIG.refreshInterval);
});

/**
 * Initialize all Chart.js charts
 */
function initializeCharts() {
    // Animal Distribution Chart (Pie)
    const animalCtx = document.getElementById('animalChart');
    if (animalCtx) {
        animalChart = new Chart(animalCtx, {
            type: 'pie',
            data: {
                labels: [],
                datasets: [{
                    data: [],
                    backgroundColor: [
                        '#4caf50', '#8bc34a', '#cddc39', 
                        '#ffc107', '#ff9800', '#ff5722'
                    ],
                    borderWidth: 2,
                    borderColor: 'rgba(10, 20, 10, 0.7)'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 15,
                            font: { size: 12 }
                        }
                    }
                }
            }
        });
    }

    // Time of Day Distribution Chart (Doughnut)
    const timeCtx = document.getElementById('timeChart');
    if (timeCtx) {
        timeChart = new Chart(timeCtx, {
            type: 'doughnut',
            data: {
                labels: [],
                datasets: [{
                    data: [],
                    backgroundColor: [
                        '#2d4a23', // Night
                        '#8c6b5d', // Day
                        '#a5d6a7'  // Dawn/Dusk
                    ],
                    borderWidth: 2,
                    borderColor: 'rgba(10, 20, 10, 0.7)'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 15,
                            font: { size: 12 }
                        }
                    }
                }
            }
        });
    }

    // Distance Over Time Chart (Line)
    const distanceCtx = document.getElementById('distanceChart');
    if (distanceCtx) {
        distanceChart = new Chart(distanceCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Proximity (cm)',
                    data: [],
                    borderColor: '#a5d6a7',
                    backgroundColor: 'rgba(165, 214, 167, 0.2)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 4,
                    pointBackgroundColor: '#a5d6a7',
                    pointBorderColor: '#fff',
                    pointHoverRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Proximity (cm)'
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Time'
                        },
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }
}

/**
 * Fetch and display main data
 */
async function loadData() {
    try {
        const response = await fetch('/api/data');
        const result = await response.json();
        
        if (result.error) {
            updateStatus('error', 'Connection Error');
            showNoDataMessage('Unable to connect to ThingSpeak. Please check your credentials.');
            return;
        }
        
        const feeds = result.feeds || [];
        
        if (feeds.length === 0) {
            updateStatus('connected', 'Connected - Awaiting Data');
            showNoDataMessage('No wildlife sightings yet. Ensure your ESP32 is active.');
        } else {
            updateStatus('connected', 'Live');
            hideNoDataMessage();
        }
        
        updateCharts(feeds);
        updateTimeline(feeds);
        
    } catch (error) {
        updateStatus('error', 'Connection Error');
        console.error('Error loading data:', error);
        showNoDataMessage('Error loading data. Check console for details.');
    }
}

/**
 * Fetch and display statistics
 */
async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        const result = await response.json();
        
        if (result.error) {
            console.error('Error loading stats:', result.error);
            return;
        }
        
        document.getElementById('totalDetections').textContent = result.total_detections || 0;
        document.getElementById('validDetections').textContent = result.valid_detections || 0;
        document.getElementById('avgDistance').textContent = result.average_distance || 0;
        document.getElementById('animalTypes').textContent = Object.keys(result.animal_counts || {}).length;
        
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

/**
 * Fetch and display latest detection
 */
async function loadLatest() {
    try {
        const response = await fetch('/api/latest');
        const result = await response.json();
        
        if (result.error || !result.latest) {
            updateLatestDetection(null);
            return;
        }
        
        updateLatestDetection(result.latest);
        
    } catch (error) {
        console.error('Error loading latest:', error);
    }
}

/**
 * Update all charts with new data
 */
function updateCharts(feeds) {
    const validFeeds = feeds.filter(f => f.is_valid_detection);
    
    // Update Animal Distribution Chart
    if (animalChart) {
        const animalCounts = {};
        validFeeds.forEach(feed => {
            const animal = feed.animal_type || 'Unknown';
            animalCounts[animal] = (animalCounts[animal] || 0) + 1;
        });
        
        animalChart.data.labels = Object.keys(animalCounts);
        animalChart.data.datasets[0].data = Object.values(animalCounts);
        animalChart.update('none');
    }
    
    // Update Time of Day Chart
    if (timeChart) {
        const timeCounts = {};
        validFeeds.forEach(feed => {
            const tod = feed.time_of_day || 'Unknown';
            timeCounts[tod] = (timeCounts[tod] || 0) + 1;
        });
        
        timeChart.data.labels = Object.keys(timeCounts);
        timeChart.data.datasets[0].data = Object.values(timeCounts);
        timeChart.update('none');
    }
    
    // Update Distance Chart
    if (distanceChart) {
        const recentFeeds = validFeeds
            .filter(f => f.distance > 0)
            .slice(0, 50)
            .reverse();
        
        distanceChart.data.labels = recentFeeds.map(f => formatTimestamp(f.timestamp, true));
        distanceChart.data.datasets[0].data = recentFeeds.map(f => f.distance);
        distanceChart.update('none');
    }
}

/**
 * Update the timeline with recent detections
 */
function updateTimeline(feeds) {
    const container = document.getElementById('timelineContainer');
    if (!container) return;
    
    const recentFeeds = feeds
        .filter(f => f.motion === 1)
        .slice(0, CONFIG.maxTimelineItems)
        .reverse();
    
    if (recentFeeds.length === 0) {
        container.innerHTML = '<div class="loading">Awaiting activity...</div>';
        return;
    }
    
    container.innerHTML = recentFeeds.map(createTimelineItem).join('');
}

/**
 * Show a no-data message
 */
function showNoDataMessage(message) {
    const container = document.querySelector('.main-grid');
    if (!container) return;

    hideNoDataMessage();
    
    const messageDiv = document.createElement('div');
    messageDiv.id = 'noDataMessage';
    messageDiv.className = 'card no-data-message';
    messageDiv.innerHTML = `
        <div class="no-data-content">
            <i class="fas fa-info-circle"></i>
            <p>${message}</p>
            <small>This is normal if your ESP32 hasn't sent any data yet.</small>
        </div>
    `;
    
    container.parentNode.insertBefore(messageDiv, container);
}

function hideNoDataMessage() {
    const message = document.getElementById('noDataMessage');
    if (message) message.remove();
}

/**
 * Create HTML for a timeline item
 */
function createTimelineItem(feed) {
    const isValid = feed.is_valid_detection;
    const isFalsePositive = feed.false_positive;
    const animal = feed.animal_type || 'Unknown';
    const distance = feed.distance > 0 ? `${feed.distance.toFixed(1)} cm` : 'N/A';
    const timeOfDay = feed.time_of_day || 'Unknown';
    
    let statusClass = 'no-motion';
    let icon = 'fa-question-circle';
    let title = 'Motion Detected';

    if (isFalsePositive) {
        statusClass = 'false-positive';
        icon = 'fa-exclamation-triangle';
        title = 'False Positive';
    } else if (isValid) {
        statusClass = 'valid';
        icon = 'fa-paw';
        title = animal;
    }
    
    return `
        <div class="timeline-item ${statusClass}">
            <div class="timeline-icon">
                <i class="fas ${icon}"></i>
            </div>
            <div class="timeline-content">
                <h4>${title}</h4>
                <p>Proximity: ${distance} | Environment: ${timeOfDay}</p>
            </div>
            <div class="timeline-time">${formatTimestamp(feed.timestamp)}</div>
        </div>
    `;
}

/**
 * Update the latest detection card
 */
function updateLatestDetection(feed) {
    const latestAnimal = document.getElementById('latestAnimal');
    const latestDistance = document.getElementById('latestDistance');
    const latestTimeOfDay = document.getElementById('latestTimeOfDay');
    const latestStatus = document.getElementById('latestStatus');
    const latestTimestamp = document.getElementById('latestTimestamp');

    if (!feed) {
        latestAnimal.textContent = 'Awaiting data...';
        latestDistance.textContent = '--';
        latestTimeOfDay.textContent = '--';
        latestStatus.textContent = '--';
        latestTimestamp.textContent = '--';
        return;
    }
    
    let status = 'Low';
    if (feed.false_positive) {
        status = 'False Positive';
    } else if (feed.is_valid_detection) {
        status = 'Confirmed';
    }
    
    latestAnimal.textContent = feed.animal_type || 'Unknown';
    latestDistance.textContent = feed.distance > 0 ? `${feed.distance.toFixed(1)} cm` : 'N/A';
    latestTimeOfDay.textContent = feed.time_of_day || 'Unknown';
    latestStatus.textContent = status;
    latestTimestamp.textContent = formatTimestamp(feed.timestamp);
}

/**
 * Update connection status indicator
 */
function updateStatus(status, text) {
    const indicator = document.getElementById('statusIndicator');
    const dot = indicator.querySelector('.status-dot');
    const textEl = document.getElementById('statusText');
    
    dot.className = 'status-dot ' + status;
    textEl.textContent = text;
}

/**
 * Format timestamp for display
 */
function formatTimestamp(timestamp, short = false) {
    if (!timestamp) return '--';
    
    try {
        const date = new Date(timestamp);
        if (isNaN(date.getTime())) return timestamp;
        
        if (short) {
            return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
        }

        const now = new Date();
        const diffMins = Math.floor((now - date) / 60000);
        
        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins} min ago`;
        
        return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
    } catch (error) {
        return timestamp;
    }
}