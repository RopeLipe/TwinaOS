// TwinaOS Installer JavaScript

let currentStep = 0;
let selectedDisk = null;
let installationData = {};

const steps = [
    'step-welcome',
    'step-locale', 
    'step-disk',
    'step-user',
    'step-summary',
    'step-install',
    'step-complete'
];

// Initialize the installer
document.addEventListener('DOMContentLoaded', function() {
    loadDisks();
    updateProgressBar();
});

// Navigation functions
function nextStep() {
    if (validateCurrentStep()) {
        if (currentStep < steps.length - 1) {
            hideCurrentStep();
            currentStep++;
            showCurrentStep();
            updateProgressBar();
            
            if (currentStep === 4) { // Summary step
                updateSummary();
            }
        }
    }
}

function prevStep() {
    if (currentStep > 0) {
        hideCurrentStep();
        currentStep--;
        showCurrentStep();
        updateProgressBar();
    }
}

function hideCurrentStep() {
    document.getElementById(steps[currentStep]).classList.add('hidden');
}

function showCurrentStep() {
    const stepElement = document.getElementById(steps[currentStep]);
    stepElement.classList.remove('hidden');
    stepElement.classList.add('fade-in');
}

function updateProgressBar() {
    const progress = ((currentStep + 1) / steps.length) * 100;
    document.getElementById('progress-bar').style.width = progress + '%';
    document.getElementById('progress-text').textContent = `Step ${currentStep + 1} of ${steps.length}`;
}

// Validation functions
function validateCurrentStep() {
    switch (currentStep) {
        case 1: // Locale step
            return document.getElementById('language').value && 
                   document.getElementById('timezone').value;
        
        case 2: // Disk step
            return selectedDisk !== null;
        
        case 3: // User step
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            const passwordConfirm = document.getElementById('password-confirm').value;
            
            if (!username || !password) {
                alert('Please fill in all required fields.');
                return false;
            }
            
            if (password !== passwordConfirm) {
                alert('Passwords do not match.');
                return false;
            }
            
            if (password.length < 6) {
                alert('Password must be at least 6 characters long.');
                return false;
            }
            
            return true;
        
        default:
            return true;
    }
}

// Disk management
async function loadDisks() {
    try {
        const response = await fetch('/api/disks');
        const disks = await response.json();
        
        const diskList = document.getElementById('disk-list');
        diskList.innerHTML = '';
        
        disks.forEach(disk => {
            const diskElement = createDiskElement(disk);
            diskList.appendChild(diskElement);
        });
    } catch (error) {
        console.error('Failed to load disks:', error);
        document.getElementById('disk-list').innerHTML = 
            '<div class="text-red-600">Failed to load available disks. Please refresh the page.</div>';
    }
}

function createDiskElement(disk) {
    const div = document.createElement('div');
    div.className = 'disk-option border border-gray-300 rounded-lg p-4 cursor-pointer';
    div.onclick = () => selectDisk(disk.device, div);
    
    div.innerHTML = `
        <div class="flex justify-between items-center">
            <div>
                <h3 class="font-semibold">${disk.device}</h3>
                <p class="text-sm text-gray-600">${disk.model || 'Unknown Model'}</p>
                <p class="text-sm text-gray-500">${formatBytes(disk.size)}</p>
            </div>
            <div class="text-right">
                <div class="w-4 h-4 border border-gray-400 rounded-full"></div>
            </div>
        </div>
    `;
    
    return div;
}

function selectDisk(device, element) {
    // Remove selection from other disks
    document.querySelectorAll('.disk-option').forEach(el => {
        el.classList.remove('selected');
        el.querySelector('.w-4').classList.remove('bg-blue-600');
    });
    
    // Select this disk
    element.classList.add('selected');
    element.querySelector('.w-4').classList.add('bg-blue-600');
    selectedDisk = device;
}

// Summary update
function updateSummary() {
    const language = document.getElementById('language');
    const timezone = document.getElementById('timezone');
    const username = document.getElementById('username').value;
    
    document.getElementById('summary-language').textContent = 
        language.options[language.selectedIndex].text;
    document.getElementById('summary-timezone').textContent = 
        timezone.options[timezone.selectedIndex].text;
    document.getElementById('summary-disk').textContent = selectedDisk;
    document.getElementById('summary-username').textContent = username;
}

// Installation process
async function startInstallation() {
    hideCurrentStep();
    currentStep++;
    showCurrentStep();
    updateProgressBar();
    
    // Prepare installation data
    installationData = {
        language: document.getElementById('language').value,
        timezone: document.getElementById('timezone').value,
        disk: selectedDisk,
        fullname: document.getElementById('fullname').value,
        username: document.getElementById('username').value,
        password: document.getElementById('password').value
    };
    
    try {
        const response = await fetch('/api/install', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(installationData)
        });
        
        if (!response.ok) {
            throw new Error('Installation request failed');
        }
        
        // Monitor installation progress
        monitorInstallation();
    } catch (error) {
        console.error('Installation failed:', error);
        addLogMessage('ERROR: Installation failed to start');
    }
}

async function monitorInstallation() {
    const eventSource = new EventSource('/api/install/progress');
    
    eventSource.onmessage = function(event) {
        const data = JSON.parse(event.data);
        
        updateInstallStatus(data.status);
        updateInstallProgress(data.progress);
        addLogMessage(data.message);
        
        if (data.progress === 100) {
            eventSource.close();
            setTimeout(() => {
                hideCurrentStep();
                currentStep++;
                showCurrentStep();
                updateProgressBar();
            }, 2000);
        }
    };
    
    eventSource.onerror = function(event) {
        console.error('Installation monitoring failed:', event);
        addLogMessage('ERROR: Lost connection to installer');
        eventSource.close();
    };
}

function updateInstallStatus(status) {
    document.getElementById('install-status').textContent = status;
}

function updateInstallProgress(progress) {
    document.getElementById('install-progress').style.width = progress + '%';
}

function addLogMessage(message) {
    const log = document.getElementById('install-log');
    const div = document.createElement('div');
    div.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
    log.appendChild(div);
    log.scrollTop = log.scrollHeight;
}

// System reboot
async function rebootSystem() {
    try {
        await fetch('/api/reboot', { method: 'POST' });
    } catch (error) {
        console.error('Reboot failed:', error);
    }
}

// Utility functions
function formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}
