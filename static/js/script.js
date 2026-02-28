
const API_BASE = '/api';

const requestCache = new Map();
const CACHE_DURATION = 15000;

let requestQueue = [];
let isProcessing = false;

function animateElement(element, animation = 'slideUp') {
    element.style.animation = 'none';
    setTimeout(() => {
        element.style.animation = `${animation} 0.5s ease-out`;
    }, 10);
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function throttle(func, limit) {
    let inThrottle;
    return function (...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

function cachedFetch(url, options = {}) {
    return fetch(url, options).then(response => response.json());
}

function clearCache(pattern = null) {
    if (pattern) {
        for (let key of requestCache.keys()) {
            if (key.includes(pattern)) {
                requestCache.delete(key);
            }
        }
    } else {
        requestCache.clear();
    }
}

document.addEventListener('DOMContentLoaded', function () {
    initializeApp();
});

function setupAutoRefresh() {

    setInterval(loadSystemStatusQuick, 20000);

    setInterval(loadUsersQuick, 30000);
}

function initializeApp() {
    setupTabs();
    loadSystemStatus();
    loadUsers();
    loadCurrentHWID();
    setupEventListeners();
    setupAutoRefresh();

    document.documentElement.style.scrollBehavior = 'smooth';
}

function setupTabs() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');

    tabButtons.forEach(button => {
        button.addEventListener('click', function () {
            const tabName = this.dataset.tab;

            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabPanes.forEach(pane => {
                pane.classList.remove('active');
            });

            this.classList.add('active');
            const targetPane = document.getElementById(tabName);
            targetPane.classList.add('active');

            setTimeout(() => {
                targetPane.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }, 50);
        });
    });
}

function loadSystemStatus() {
    fetch(`${API_BASE}/system/status`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const totalUsersEl = document.getElementById('totalUsers');
                if (totalUsersEl) totalUsersEl.textContent = data.total_users;

                const systemStatusEl = document.getElementById('systemStatus');
                if (systemStatusEl) systemStatusEl.textContent = '[OK] Running';
            }
        })
        .catch(error => console.error('Error loading status:', error));
}

function loadSystemStatusQuick() {
    cachedFetch(`${API_BASE}/system/status`)
        .then(data => {
            if (data.success && data.total_users !== window.lastUserCount) {
                const totalUsersEl = document.getElementById('totalUsers');
                if (totalUsersEl) totalUsersEl.textContent = data.total_users;
                window.lastUserCount = data.total_users;
            }
        })
        .catch(error => console.error('Error loading status:', error));
}

function loadUsers() {
    if (typeof loadDashboardData === 'function') {
        loadDashboardData();
    }
}

function loadUsersQuick() {
    if (typeof loadDashboardData === 'function') {
        loadDashboardData();
    }
}

function setupEventListeners() {

    const createForm = document.getElementById('createUserForm');
    if (createForm) {
        createForm.addEventListener('submit', function (e) {
            e.preventDefault();
            const username = document.getElementById('newUsername').value;
            generateLicenseForUser(username);
        });
    }

    const checkLicenseForm = document.getElementById('checkLicenseForm');
    if (checkLicenseForm) {
        checkLicenseForm.addEventListener('submit', function (e) {
            e.preventDefault();
            const licenseKey = document.getElementById('lookupLicenseKey').value;
            checkLicenseStatus(licenseKey);
        });
    }

    const enrollForm = document.getElementById('enrollForm');
    if (enrollForm) {
        enrollForm.addEventListener('submit', function (e) {
            e.preventDefault();
            const username = document.getElementById('enrollUsername').value;
            const numSessions = parseInt(document.getElementById('enrollSessions').value) || 5;
            const duration = parseInt(document.getElementById('enrollDuration').value) || 30;
            enrollUser(username, numSessions, duration);
        });
    }

    const authForm = document.getElementById('authenticateForm');
    if (authForm) {
        authForm.addEventListener('submit', function (e) {
            e.preventDefault();
            const username = document.getElementById('authUsername').value;
            const duration = parseInt(document.getElementById('authDuration').value) || 30;
            authenticateUser(username, duration);
        });
    }

    const userInfoForm = document.getElementById('userInfoForm');
    if (userInfoForm) {
        userInfoForm.addEventListener('submit', function (e) {
            e.preventDefault();
            const username = document.getElementById('infoUsername').value;
            viewUserInfo(username);
        });
    }

    const verifyHwidForm = document.getElementById('verifyHwidForm');
    if (verifyHwidForm) {
        verifyHwidForm.addEventListener('submit', function (e) {
            e.preventDefault();
            const username = document.getElementById('hwidUsername').value;
            verifyHWID(username);
        });
    }

   
    const inspectSecurityForm = document.getElementById('inspectSecurityForm');
    if (inspectSecurityForm) {
        inspectSecurityForm.addEventListener('submit', function (e) {
            e.preventDefault();
            const username = document.getElementById('inspectUsername').value;
            inspectUserSecurity(username);
        });
    }

   
    setInterval(loadSecurityBlocks, 30000);
    loadSecurityBlocks();
}

function generateLicenseForUser(username) {
    if (!username) {
        showAlert('[WARNING] Username cannot be empty!', 'error');
        return;
    }

    const btn = event.target.querySelector('button');
    const originalText = btn.textContent;
    btn.disabled = true;
    btn.textContent = 'Generating...';

    const payload = {
        owner: username,
        max_users: 1,
        tier: 'basic'
    };

    fetch(`${API_BASE}/licenses/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                let successMsg = `[OK] Generated License for ${username}`;

                const formSection = document.getElementById('createUserForm').parentElement;
                const existingResult = document.getElementById('createUserResult');
                if (existingResult) existingResult.remove();

                const resultDiv = document.createElement('div');
                resultDiv.id = 'createUserResult';
                resultDiv.className = 'result-message success show';
                resultDiv.style.marginTop = '15px';
                resultDiv.innerHTML = `
                    <strong>✅ License Generated Successfully</strong><br><br>
                    <div style="background: rgba(0,0,0,0.2); padding: 10px; border-radius: 5px; margin-top: 10px;">
                        <div style="color: var(--accent-color); font-weight: bold; margin-bottom: 5px;">License Key for <strong>${username}</strong>:</div>
                        <code style="display: block; word-break: break-all; color: white;">${data.license_key}</code>
                        <div style="margin-top: 10px; font-size: 0.9em; display: flex; gap: 15px;">
                            <span><span style="color: var(--success-color)">●</span> Status: Active</span>
                            <span>⌛ Expiry: Never</span>
                            <span>⭐ Tier: Basic (1 User)</span>
                        </div>
                    </div>
                `;
                formSection.appendChild(resultDiv);

                document.getElementById('newUsername').value = '';
                clearCache('users');
                loadUsers();
            } else {
                showAlert(`[ERROR] ${data.error}`, 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('[ERROR] Error generating license', 'error');
        })
        .finally(() => {
            btn.disabled = false;
            btn.textContent = originalText;
        });
}

function checkLicenseStatus(licenseKey) {
    if (!licenseKey) {
        showAlert('[WARNING] License key cannot be empty!', 'error');
        return;
    }

    const resultDiv = document.getElementById('licenseStatusResult');
    resultDiv.innerHTML = '<p class="loading">[WAIT] Checking license status...</p>';
    resultDiv.classList.add('show');

    cachedFetch(`${API_BASE}/licenses/info/${licenseKey}`)
        .then(data => {
            if (data.success) {
                const license = data.license;

                const expiresAtRaw = license.expires_at || null;
                const expiresText = (expiresAtRaw && expiresAtRaw !== 'Never') ? new Date(expiresAtRaw).toLocaleString() : 'Never';

                let statusLabel = 'Active';
                if (!license.active) {
                    statusLabel = 'Inactive / Revoked';
                } else if (expiresAtRaw && expiresAtRaw !== 'Never' && new Date(expiresAtRaw) < new Date()) {
                    statusLabel = 'Expired';
                }

                const statusColor = statusLabel === 'Active' ? '#10B981' : (statusLabel === 'Expired' ? '#F59E0B' : '#EF4444');
                const activeUsersArray = Array.isArray(license.active_users) ? license.active_users : [];

                resultDiv.innerHTML = `
                    <div style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 8px; border: 1px solid ${statusColor}; border-left: 4px solid ${statusColor}; text-align: left;">
                        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 15px; margin-bottom: 15px;">
                            <div>
                                <h4 style="margin: 0; color: var(--accent-light); font-size: 1.1em;">License Details</h4>
                                <code style="display: block; margin-top: 5px; color: #94A3B8;">${license.key}</code>
                            </div>
                            <span style="background: ${statusColor}; color: white; padding: 6px 12px; border-radius: 4px; font-weight: bold; font-size: 0.9em;">
                                ${statusLabel}
                            </span>
                        </div>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                            <p style="margin: 0; color: #cbd5e1;"><strong>Owner:</strong> ${license.owner}</p>
                            <p style="margin: 0; color: #cbd5e1;"><strong>Tier:</strong> ${String(license.tier || 'basic').toUpperCase()}</p>
                            <p style="margin: 0; color: #cbd5e1;"><strong>Used Slots:</strong> ${activeUsersArray.length} / ${license.max_users}</p>
                            <p style="margin: 0; color: #cbd5e1;"><strong>Expiry:</strong> ${expiresText}</p>
                        </div>
                        ${activeUsersArray.length > 0 ? `
                        <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid rgba(255,255,255,0.1);">
                            <p style="margin: 0; color: #94A3B8; font-size: 0.85em;">Active Associated Users:</p>
                            <div style="display: flex; gap: 5px; flex-wrap: wrap; margin-top: 5px;">
                                ${activeUsersArray.map(u => `<span style="background: rgba(6, 182, 212, 0.15); color: #06B6D4; padding: 3px 8px; border-radius: 3px; font-size: 0.85em;">👤 ${u}</span>`).join('')}
                            </div>
                        </div>` : ''}
                    </div>
                `;
            } else {
                resultDiv.innerHTML = `<div class="result-message error show">[ERROR] ${data.error}</div>`;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            resultDiv.innerHTML = `<div class="result-message error show">[ERROR] Error checking license</div>`;
        });
}

function enrollUser(username, numSessions, duration) {
    if (!username) {
        showAlert('[WARNING] Username cannot be empty!', 'error');
        return;
    }

    const resultDiv = document.getElementById('enrollResult');
    resultDiv.innerHTML = '<p class="loading">[WAIT] Enrolling user... This may take a moment.</p>';
    resultDiv.classList.add('show');

    fetch(`${API_BASE}/user/${username}/enroll`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ num_sessions: numSessions, session_duration: duration })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                resultDiv.innerHTML = `<div class="result-message success show">[OK] ${data.message}</div>`;
                clearCache('users');
                loadDashboardData();
                setTimeout(() => {
                    resultDiv.innerHTML = '';
                    resultDiv.classList.remove('show');
                }, 5000);
            } else {
                resultDiv.innerHTML = `<div class="result-message error show">[ERROR] ${data.error}</div>`;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            resultDiv.innerHTML = `<div class="result-message error show">[ERROR] Error enrolling user</div>`;
        });
}

function authenticateUser(username, duration) {
    if (!username) {
        showAlert('[WARNING] Username cannot be empty!', 'error');
        return;
    }

    const resultDiv = document.getElementById('authResult');
    resultDiv.innerHTML = '<p class="loading">[WAIT] Authenticating user... This may take a moment.</p>';
    resultDiv.classList.add('show');

    fetch(`${API_BASE}/user/${username}/authenticate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_duration: duration })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const messageClass = data.authenticated ? 'success' : 'error';
                const icon = data.authenticated ? '[OK]' : '[FAIL]';

               
                let chartHtml = '';
                if (data.confidence !== undefined && data.breakdown) {
                    chartHtml = `
                        <div class="chart-container">
                            <div class="chart-box">
                                <canvas id="overallConfidenceChart"></canvas>
                            </div>
                            <div class="chart-box">
                                <canvas id="breakdownPieChart"></canvas>
                            </div>
                        </div>
                    `;
                }

                resultDiv.innerHTML = `
                    <div class="result-message ${messageClass} show" style="margin-bottom: 0;">
                        ${icon} ${data.message}
                    </div>
                    ${chartHtml}
                `;

                clearCache('users');
                loadDashboardData();

                if (data.confidence !== undefined && data.breakdown) {
                    const ctxBar = document.getElementById('overallConfidenceChart').getContext('2d');
                    new Chart(ctxBar, {
                        type: 'bar',
                        data: {
                            labels: ['Total Match %'],
                            datasets: [{
                                label: 'Model Confidence',
                                data: [data.confidence],
                                backgroundColor: data.authenticated ? 'rgba(16, 185, 129, 0.6)' : 'rgba(239, 68, 68, 0.6)',
                                borderColor: data.authenticated ? 'rgba(16, 185, 129, 1)' : 'rgba(239, 68, 68, 1)',
                                borderWidth: 1
                            }]
                        },
                        options: {
                            responsive: true,
                            scales: {
                                y: {
                                    beginAtZero: true,
                                    max: 100
                                }
                            }
                        }
                    });

                    const ctxPie = document.getElementById('breakdownPieChart').getContext('2d');
                    new Chart(ctxPie, {
                        type: 'pie',
                        data: {
                            labels: ['Keystroke Rhythm', 'Mouse Dynamics'],
                            datasets: [{
                                data: [data.breakdown.keystroke, data.breakdown.mouse],
                                backgroundColor: [
                                    'rgba(59, 130, 246, 0.7)',
                                    'rgba(245, 158, 11, 0.7)'
                                ],
                                borderColor: [
                                    'rgba(59, 130, 246, 1)',
                                    'rgba(245, 158, 11, 1)'
                                ],
                                borderWidth: 1
                            }]
                        },
                        options: {
                            responsive: true,
                            plugins: {
                                title: {
                                    display: true,
                                    text: 'Behavioral Components'
                                }
                            }
                        }
                    });
                }
            } else {
                resultDiv.innerHTML = `<div class="result-message error show">[ERROR] ${data.error}</div>`;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            resultDiv.innerHTML = `<div class="result-message error show">[ERROR] Error authenticating user</div>`;
        });
}

function viewUserInfo(username) {
    if (!username) {
        showAlert('[WARNING] Username cannot be empty!', 'error');
        return;
    }

    const resultDiv = document.getElementById('userInfoResult');
    resultDiv.innerHTML = '<p class="loading">[WAIT] Loading user information...</p>';

    cachedFetch(`${API_BASE}/user/${username}`)
        .then(data => {
            if (data.success) {
                const user = data.user;
                resultDiv.innerHTML = `
                    <div class="user-info-details">
                        <p><strong>Username:</strong> ${user.username || 'N/A'}</p>
                        <p><strong>Status:</strong> ${user.status || 'Active'}</p>
                        <p><strong>Enrolled:</strong> ${user.enrolled ? '[OK] Yes' : '[NO] No'}</p>
                        <p><strong>Created:</strong> ${user.created_at || 'N/A'}</p>
                        <p><strong>Device HWID:</strong> <code style="word-break: break-all; background: rgba(59,130,246,0.1); padding: 4px; border-radius: 3px;">${user.hwid || 'N/A'}</code></p>
                    </div>
                `;
            } else {
                resultDiv.innerHTML = `<div class="result-message error show">[ERROR] ${data.error}</div>`;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            resultDiv.innerHTML = `<div class="result-message error show">[ERROR] Error loading user info</div>`;
        });
}

function deleteUser(username) {
    if (!confirm(`Are you sure you want to delete user "${username}"?`)) {
        return;
    }

    fetch(`${API_BASE}/user/${username}/delete`, {
        method: 'DELETE'
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showAlert(`[OK] ${data.message}`, 'success');
                clearCache('users');
                loadUsers();
                loadSystemStatus();
            } else {
                showAlert(`[ERROR] ${data.error}`, 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('[ERROR] Error deleting user', 'error');
        });
}

function showAlert(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    toast.style.animation = 'slideInRight 0.4s ease-out';

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideOutRight 0.4s ease-out';
        setTimeout(() => toast.remove(), 400);
    }, 4000);
}

function loadCurrentHWID() {
    cachedFetch(`${API_BASE}/hwid/current`)
        .then(data => {
            if (data.success) {
                const hwidDiv = document.getElementById('hwidInfo');
                if (hwidDiv) {
                    hwidDiv.innerHTML = `
                        <p><strong>Username:</strong> ${data.info?.username || 'unknown'}</p>
                        <p><strong>Device HWID (SID):</strong> <code style="word-break: break-all; background: rgba(59,130,246,0.1); padding: 4px; border-radius: 3px;">${data.hwid_short || 'unknown'}</code></p>
                        <details style="margin-top: 15px;">
                            <summary style="cursor: pointer; color: #94A3B8;">View Raw Output</summary>
                            <pre style="background: rgba(0,0,0,0.3); padding: 10px; border-radius: 5px; color: #cbd5e1; font-size: 0.85em; overflow-x: auto; margin-top: 10px;">${data.info?.raw || 'N/A'}</pre>
                        </details>
                        <p style="font-size: 0.85em; opacity: 0.8; margin-top: 15px;">This is your unique device fingerprint and SID from the local machine.</p>
                    `;
                }
            } else {
                const hwidDiv = document.getElementById('hwidInfo');
                if (hwidDiv) {
                    hwidDiv.innerHTML = `<p class="error" style="color: var(--danger-color);">Error loading HWID: ${data.error}</p>`;
                }
            }
        })
        .catch(error => {
            console.error('Error loading HWID:', error);
            const hwidDiv = document.getElementById('hwidInfo');
            if (hwidDiv) {
                hwidDiv.innerHTML = `<p class="error" style="color: var(--danger-color);">Failed to fetch HWID information.</p>`;
            }
        });
}

function verifyHWID(username) {
    if (!username) {
        showAlert('[WARNING] Username cannot be empty!', 'error');
        return;
    }

    const resultDiv = document.getElementById('hwidVerifyResult');
    resultDiv.innerHTML = '<p class="loading">[WAIT] Verifying device...</p>';
    resultDiv.classList.add('show');

    cachedFetch(`${API_BASE}/hwid/verify/${username}`)
        .then(data => {
            if (data.success) {
                if (data.hwid_match) {
                    resultDiv.innerHTML = `<div class="result-message success show">
                        [OK] Device Authorized!
                        <br>User '${data.username}' - Device is registered to this account
                    </div>`;
                } else {
                    resultDiv.innerHTML = `<div class="result-message error show">
                        [FAIL] Device Mismatch!
                        <br>This device is not registered for user '${data.username}'
                        <br><small>Registered: ${data.stored_hwid} | This Device: ${data.current_hwid}</small>
                    </div>`;
                }
                setTimeout(() => {
                    resultDiv.innerHTML = '';
                    resultDiv.classList.remove('show');
                }, 7000);
            } else {
                resultDiv.innerHTML = `<div class="result-message error show">[ERROR] ${data.error}</div>`;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            resultDiv.innerHTML = `<div class="result-message error show">[ERROR] Error verifying device</div>`;
        });
}

function loadSecurityBlocks() {
   
    const resultsTab = document.getElementById('security-results');
    if (resultsTab && !resultsTab.classList.contains('active')) return;

    cachedFetch(`${API_BASE}/dashboard/data`)
        .then(data => {
            if (data.success && data.all_users) {
               
               
                const blocksList = document.getElementById('securityBlocksList');
                const totalBlocks = data.stats?.fraud_blocks || 0;

                if (totalBlocks === 0) {
                    blocksList.innerHTML = '<p class="loading" style="color:var(--text-color)">✅ No malicious bots or fraud attempts detected recently.</p>';
                    return;
                }

               
                blocksList.innerHTML = `
                    <div class="user-item" style="border-left: 4px solid var(--danger-color);">
                        <div class="user-item-info">
                            <div class="user-item-name" style="color: var(--danger-color)">🚨 Fraudulent Attempts Blocked</div>
                            <div class="user-item-status">Total Blocks Detected:</div>
                        </div>
                        <div class="user-item-actions">
                            <span style="font-size: 1.5em; font-weight: bold; color: var(--danger-color)">${totalBlocks}</span>
                        </div>
                    </div>
                `;
            }
        })
        .catch(error => {
            console.error('Error loading blocks:', error);
        });
}

function inspectUserSecurity(username) {
    if (!username) {
        showAlert('[WARNING] Username cannot be empty!', 'error');
        return;
    }

    const resultDiv = document.getElementById('securityReportResult');
    resultDiv.innerHTML = '<p class="loading">[WAIT] Generating Security Report...</p>';
    resultDiv.classList.add('show');

    cachedFetch(`${API_BASE}/user/profile`)
        .then(data => {
           
           
            return cachedFetch(`${API_BASE}/user/${username}`);
        })
        .then(data => {
            if (data && data.success) {
                const user = data.user;
                const score = user.security_score || 0;
                let scoreColor = 'var(--danger-color)';
                if (score > 40) scoreColor = 'var(--warning-color)';
                if (score > 80) scoreColor = 'var(--success-color)';

                const enrolledStatus = user.enrolled
                    ? '<span style="color:var(--success-color)">[OK] Enrolled (AI Model Active)</span>'
                    : '<span style="color:var(--danger-color)">[WARN] Missing AI Behavioral Profile</span>';

                let lastLoginHtml = '<div style="color: #94A3B8; font-style: italic; background: rgba(0,0,0,0.3); padding: 10px; border-radius: 5px;">No authentication tests recorded yet</div>';
                if (user.activity_summary && user.activity_summary.last_login) {
                    const ll = user.activity_summary.last_login;
                    const authColor = ll.success ? '#10B981' : '#EF4444';
                    const authText = ll.success ? 'Success (Human ✅)' : 'Blocked (Robot 🚨)';
                    const scoreText = ll.behavioral_score ? (ll.behavioral_score * 100).toFixed(1) + '%' : 'N/A';
                    lastLoginHtml = `
                        <div style="background: rgba(0,0,0,0.3); padding: 15px; border-radius: 5px; border-left: 4px solid ${authColor};">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
                                <div style="color: ${authColor}; font-weight: bold; font-size: 1.1em;">${authText}</div>
                                <div style="color: #94A3B8; font-size: 0.85em;">${new Date(ll.timestamp).toLocaleString()}</div>
                            </div>
                            <div style="color: #cbd5e1; font-size: 0.95em;">
                                Match Confidence: <span style="font-weight: bold; color: #06B6D4;">${scoreText}</span>
                            </div>
                        </div>
                    `;
                }

                resultDiv.innerHTML = `
                    <div style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 8px; border: 1px solid var(--border-color);">
                        <h4 style="margin-top:0; color: var(--accent-light);">🛡️ Security Report for: ${user.username}</h4>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top:15px; padding-bottom: 15px; border-bottom: 1px solid rgba(255,255,255,0.1);">
                            <div>
                                <p style="margin: 5px 0; color: #aaa; font-size: 0.9em;">Overall Security Score</p>
                                <div style="font-size: 2em; font-weight: bold; color: ${scoreColor}">${score.toFixed(1)} / 100</div>
                            </div>
                            <div>
                                <p style="margin: 5px 0; color: #aaa; font-size: 0.9em;">AI Training Status</p>
                                <div>${enrolledStatus}</div>
                            </div>
                        </div>

                        <h5 style="margin-top: 15px; margin-bottom: 10px; color: #cbd5e1;">More User Info</h5>
                        <div style="background: rgba(0,0,0,0.3); padding: 10px; border-radius: 5px; margin-bottom: 15px;">
                            <div style="color: #94A3B8; font-size: 0.85em; margin-bottom: 2px;">Device HWID</div>
                            <code style="display: block; word-break: break-all; color: #60A5FA;">${user.hwid || 'N/A'}</code>
                            <div style="color: #94A3B8; font-size: 0.85em; margin-top: 8px; margin-bottom: 2px;">Account Created</div>
                            <div style="color: #E2E8F0; font-size: 0.9em;">${user.created_at ? new Date(user.created_at).toLocaleString() : 'N/A'}</div>
                        </div>
                        
                        <h5 style="margin-top: 15px; margin-bottom: 10px; color: #cbd5e1;">Latest Authentication Test</h5>
                        ${lastLoginHtml}

                        
                        <h5 style="margin-top: 15px; margin-bottom: 10px; color: #cbd5e1;">Detailed Activity Analysis</h5>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                            <div style="background: rgba(0,0,0,0.3); padding: 10px; border-radius: 5px;">
                                <div style="color: #94A3B8; font-size: 0.85em; margin-bottom: 5px;">Total Activities</div>
                                <div style="font-size: 1.2em; font-weight: bold; color: #E2E8F0;">${(user.activity_summary && user.activity_summary.total_activities) || 0}</div>
                            </div>
                            <div style="background: rgba(0,0,0,0.3); padding: 10px; border-radius: 5px;">
                                <div style="color: #94A3B8; font-size: 0.85em; margin-bottom: 5px;">Login Success Rate</div>
                                <div style="font-size: 1.2em; font-weight: bold; color: #10B981;">${((user.activity_summary && user.activity_summary.success_rate) || 0).toFixed(1)}%</div>
                            </div>
                            <div style="background: rgba(0,0,0,0.3); padding: 10px; border-radius: 5px;">
                                <div style="color: #94A3B8; font-size: 0.85em; margin-bottom: 5px;">Successful Logins</div>
                                <div style="font-size: 1.2em; font-weight: bold; color: #10B981;">${(user.activity_summary && user.activity_summary.successful_logins) || 0}</div>
                            </div>
                            <div style="background: rgba(0,0,0,0.3); padding: 10px; border-radius: 5px;">
                                <div style="color: #94A3B8; font-size: 0.85em; margin-bottom: 5px;">Failed Logins</div>
                                <div style="font-size: 1.2em; font-weight: bold; color: #EF4444;">${(user.activity_summary && user.activity_summary.failed_logins) || 0}</div>
                            </div>
                        </div>
                        
                        <div style="margin-top: 15px; background: rgba(0,0,0,0.3); padding: 10px; border-radius: 5px;">
                            <div style="color: #94A3B8; font-size: 0.85em; margin-bottom: 5px;">Average Behavioral Match Score</div>
                            <div style="display: flex; align-items: center; gap: 10px;">
                                <div style="flex-grow: 1; height: 8px; background: #1E3A5F; border-radius: 4px; overflow: hidden;">
                                    <div style="height: 100%; background: linear-gradient(90deg, #10B981, #06B6D4); width: ${((user.activity_summary && user.activity_summary.avg_score) || 0) * 100}%;"></div>
                                </div>
                                <div style="font-size: 1.1em; font-weight: bold; color: #06B6D4;">${(((user.activity_summary && user.activity_summary.avg_score) || 0) * 100).toFixed(1)}%</div>
                            </div>
                        </div>
                        
                    </div>
                `;
            } else {
                resultDiv.innerHTML = `<div class="result-message error show">[ERROR] Could not fetch data for ${username}</div>`;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            resultDiv.innerHTML = `<div class="result-message error show">[ERROR] Error generating report</div>`;
        });
}

try {
    if (typeof io !== 'undefined') {
        const socket = io();
        socket.on('connect', () => console.log('[socket] connected'));
        socket.on('user_update', (data) => {
            if (data && data.users) {
                displayUsers(data.users);
                const el = document.getElementById('totalUsers');
                if (el) el.textContent = data.users.length;
                window.lastUserList = data.users;
            }
        });

        socket.on('enroll_result', (data) => {
            if (data && data.username) {
                const msg = data.success ? `Enrollment complete for ${data.username}` : `Enrollment failed for ${data.username}`;
                showAlert(msg, data.success ? 'success' : 'error');

                if (data.success) {
                    clearCache('users');
                    loadUsersQuick();
                    loadSystemStatusQuick && loadSystemStatusQuick();
                }
            }
        });
        socket.on('auth_result', (data) => {
            if (data && data.username) {
                const msg = data.authenticated ? `Authentication succeeded for ${data.username}` : `Authentication failed for ${data.username}`;
                showAlert(msg, data.authenticated ? 'success' : 'error');
            }
        });
    }
} catch (e) {

}

document.addEventListener('DOMContentLoaded', () => {
    try {
        const userBadge = document.querySelector('.user-badge');
        if (userBadge && typeof fetch === 'function') {
            fetch('/api/system/status').then(r => r.json()).then(j => {

            }).catch(() => { });
        }
    } catch (e) { }
});

// ----------------------------------------------------
// Security Results Tab Functions
// ----------------------------------------------------
function inspectUserSecurity(username) {
    const resultDiv = document.getElementById('securityReportResult');
    if (!resultDiv) return;

    resultDiv.innerHTML = '<p class="loading">Fetching security profile...</p>';
    resultDiv.className = 'result-message';

    fetch(`${API_BASE}/user/${username}`)
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                const user = data.user;
                let html = `<h4>✅ User Found: ${user.username}</h4>`;
                html += `<p><strong>HWID:</strong> ${user.hwid || 'N/A'}</p>`;
                html += `<p><strong>Enrolled for AI Auth:</strong> ${user.enrolled ? 'Yes' : 'No'}</p>`;

                resultDiv.innerHTML = html;
                resultDiv.classList.add('success');
            } else {
                resultDiv.innerHTML = `❌ Error: ${data.error}`;
                resultDiv.classList.add('error');
            }
        })
        .catch(err => {
            resultDiv.innerHTML = `❌ Request failed: ${err.message}`;
            resultDiv.classList.add('error');
        });
}

function loadSecurityBlocks() {
    const list = document.getElementById('securityBlocksList');
    if (list && list.innerHTML.includes('Loading')) {
        list.innerHTML = '<p class="muted">No recent blocks detected.</p>';
    }
}
