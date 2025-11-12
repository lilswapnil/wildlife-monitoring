/**
 * Wildlife Monitoring Dashboard - Frontend JavaScript
 * Handles data fetching, chart rendering, and real-time updates
 */

// Chart instances
let animalChart = null;
let timeChart = null;
let distanceChart = null;

// Configuration
const CONFIG = {
    refreshInterval: 30000, // 30 seconds
    maxTimelineItems: 20
};

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    console.log('Wildlife Monitoring Dashboard initialized');
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
                        '#667eea',
                        '#764ba2',
                        '#f093fb',
                        '#4facfe',
                        '#43e97b',
                        '#f5576c'
                    ],
                    borderWidth: 2,
                    borderColor: '#fff'
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
                            font: {
                                size: 12
                            }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.parsed || 0;
                                return `${label}: ${value} detection${value !== 1 ? 's' : ''}`;
                            }
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
                        '#2c3e50', // Night
                        '#3498db', // Day
                        '#f39c12'  // Dawn/Dusk
                    ],
                    borderWidth: 2,
                    borderColor: '#fff'
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
                            font: {
                                size: 12
                            }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.parsed || 0;
                                return `${label}: ${value} detection${value !== 1 ? 's' : ''}`;
                            }
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
                    label: 'Distance (cm)',
                    data: [],
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 4,
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
                            text: 'Distance (cm)'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Time'
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `Distance: ${context.parsed.y} cm`;
                            }
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
            console.error('Error:', result.error);
            showNoDataMessage('Unable to connect to ThingSpeak. Please check your credentials.');
            return;
        }
        
        const feeds = result.feeds || [];
        
        if (feeds.length === 0) {
            updateStatus('connected', 'Connected - Waiting for Data');
            showNoDataMessage('No wildlife detections yet. Make sure your ESP32 is running and uploading data to ThingSpeak.');
            updateCharts(feeds);
            updateTimeline(feeds);
        } else {
            updateStatus('connected', 'Connected');
            hideNoDataMessage();
            updateCharts(feeds);
            updateTimeline(feeds);
        }
        
    } catch (error) {
        updateStatus('error', 'Connection Error');
        console.error('Error loading data:', error);
        showNoDataMessage('Error loading data. Please check the console for details.');
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
        
        // Update stat cards
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
    // Filter valid detections only
    const validFeeds = feeds.filter(f => f.is_valid_detection);
    
    // Update Animal Distribution Chart
    if (animalChart) {
        const animalCounts = {};
        validFeeds.forEach(feed => {
            const animal = feed.animal_type || 'Unknown';
            animalCounts[animal] = (animalCounts[animal] || 0) + 1;
        });
        
        const labels = Object.keys(animalCounts);
        const data = Object.values(animalCounts);
        
        // If no data, show empty chart with message
        if (labels.length === 0) {
            animalChart.data.labels = ['No Data Yet'];
            animalChart.data.datasets[0].data = [1];
            animalChart.data.datasets[0].backgroundColor = ['#e0e0e0'];
        } else {
            animalChart.data.labels = labels;
            animalChart.data.datasets[0].data = data;
            animalChart.data.datasets[0].backgroundColor = [
                '#667eea',
                '#764ba2',
                '#f093fb',
                '#4facfe',
                '#43e97b',
                '#f5576c'
            ];
        }
        animalChart.update('none'); // 'none' mode for smooth updates
    }
    
    // Update Time of Day Chart
    if (timeChart) {
        const timeCounts = {};
        validFeeds.forEach(feed => {
            const tod = feed.time_of_day || 'Unknown';
            timeCounts[tod] = (timeCounts[tod] || 0) + 1;
        });
        
        const labels = Object.keys(timeCounts);
        const data = Object.values(timeCounts);
        
        // If no data, show empty chart
        if (labels.length === 0) {
            timeChart.data.labels = ['No Data Yet'];
            timeChart.data.datasets[0].data = [1];
            timeChart.data.datasets[0].backgroundColor = ['#e0e0e0'];
        } else {
            timeChart.data.labels = labels;
            timeChart.data.datasets[0].data = data;
            timeChart.data.datasets[0].backgroundColor = [
                '#2c3e50', // Night
                '#3498db', // Day
                '#f39c12'  // Dawn/Dusk
            ];
        }
        timeChart.update('none');
    }
    
    // Update Distance Chart (show last 50 valid detections)
    if (distanceChart) {
        const recentFeeds = validFeeds
            .filter(f => f.distance > 0)
            .slice(0, 50)
            .reverse(); // Most recent first
        
        const labels = recentFeeds.map(f => formatTimestamp(f.timestamp));
        const distances = recentFeeds.map(f => f.distance);
        
        distanceChart.data.labels = labels;
        distanceChart.data.datasets[0].data = distances;
        distanceChart.update('none');
    }
}

/**
 * Update the timeline with recent detections
 */
function updateTimeline(feeds) {
    const container = document.getElementById('timelineContainer');
    if (!container) return;
    
    // Get recent detections (most recent first)
    const recentFeeds = feeds
        .filter(f => f.motion === 1) // Only show motion detections
        .slice(0, CONFIG.maxTimelineItems)
        .reverse();
    
    if (recentFeeds.length === 0) {
        container.innerHTML = '<div class="loading">No detections yet. Waiting for ESP32 to send data...</div>';
        return;
    }
    
    container.innerHTML = recentFeeds.map(feed => createTimelineItem(feed)).join('');
}

/**
 * Show a no-data message on the dashboard
 */
function showNoDataMessage(message) {
    // Remove any existing message
    hideNoDataMessage();
    
    // Create message element
    const messageDiv = document.createElement('div');
    messageDiv.id = 'noDataMessage';
    messageDiv.className = 'no-data-message';
    messageDiv.innerHTML = `
        <div class="no-data-content">
            <i class="fas fa-info-circle"></i>
            <p>${message}</p>
            <small>This is normal if your ESP32 hasn't sent any data yet.</small>
        </div>
    `;
    
    // Insert after the latest detection card
    const latestCard = document.getElementById('latestCard');
    if (latestCard && latestCard.parentNode) {
        latestCard.parentNode.insertBefore(messageDiv, latestCard.nextSibling);
    }
}

/**
 * Hide the no-data message
 */
function hideNoDataMessage() {
    const message = document.getElementById('noDataMessage');
    if (message) {
        message.remove();
    }
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
    const timestamp = formatTimestamp(feed.timestamp);
    
    let statusClass = 'valid';
    let statusText = 'Valid Detection';
    let icon = 'fa-check-circle';
    
    if (isFalsePositive) {
        statusClass = 'false-positive';
        statusText = 'False Positive';
        icon = 'fa-exclamation-triangle';
    } else if (!isValid) {
        statusClass = '';
        statusText = 'No Motion';
        icon = 'fa-minus-circle';
    }
    
    return `
        <div class="timeline-item ${statusClass}">
            <div class="timeline-icon">
                <i class="fas ${icon}"></i>
            </div>
            <div class="timeline-content">
                <h4>${animal}</h4>
                <p>Distance: ${distance} | Time: ${timeOfDay}</p>
            </div>
            <div class="timeline-time">${timestamp}</div>
        </div>
    `;
}

/**
 * Update the latest detection card
 */
function updateLatestDetection(feed) {
    if (!feed) {
        document.getElementById('latestAnimal').textContent = 'No detections yet';
        document.getElementById('latestDistance').textContent = '--';
        document.getElementById('latestTimeOfDay').textContent = '--';
        document.getElementById('latestStatus').textContent = 'Waiting for data';
        document.getElementById('latestTimestamp').textContent = '--';
        return;
    }
    
    const animal = feed.animal_type || 'Unknown';
    const distance = feed.distance > 0 ? `${feed.distance.toFixed(1)} cm` : 'N/A';
    const timeOfDay = feed.time_of_day || 'Unknown';
    const timestamp = formatTimestamp(feed.timestamp);
    
    let status = 'No Detection';
    if (feed.false_positive) {
        status = 'False Positive';
    } else if (feed.is_valid_detection) {
        status = 'Valid Detection';
    }
    
    document.getElementById('latestAnimal').textContent = animal;
    document.getElementById('latestDistance').textContent = distance;
    document.getElementById('latestTimeOfDay').textContent = timeOfDay;
    document.getElementById('latestStatus').textContent = status;
    document.getElementById('latestTimestamp').textContent = timestamp;
}

/**
 * Update connection status indicator
 */
function updateStatus(status, text) {
    const indicator = document.getElementById('statusIndicator');
    const dot = indicator.querySelector('.status-dot');
    const textEl = document.getElementById('statusText');
    
    if (dot) {
        dot.className = 'status-dot ' + status;
    }
    if (textEl) {
        textEl.textContent = text;
    }
}

/**
 * Format timestamp for display
 */
function formatTimestamp(timestamp) {
    if (!timestamp) return '--';
    
    try {
        const date = new Date(timestamp);
        if (isNaN(date.getTime())) {
            return timestamp; // Return as-is if not a valid date
        }
        
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);
        
        // Show relative time if recent
        if (diffMins < 1) {
            return 'Just now';
        } else if (diffMins < 60) {
            return `${diffMins} min${diffMins !== 1 ? 's' : ''} ago`;
        } else if (diffHours < 24) {
            return `${diffHours} hour${diffHours !== 1 ? 's' : ''} ago`;
        } else if (diffDays < 7) {
            return `${diffDays} day${diffDays !== 1 ? 's' : ''} ago`;
        }
        
        // Otherwise show formatted date
        return date.toLocaleString('en-US', {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    } catch (error) {
        return timestamp;
    }
}

