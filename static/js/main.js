document.addEventListener('DOMContentLoaded', function() {
    // Theme toggle functionality
    const themeSwitch = document.getElementById('themeSwitch');
    
    // Check for saved theme preference or respect OS preference
    const prefersDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const savedTheme = localStorage.getItem('theme');
    
    if (savedTheme === 'dark' || (!savedTheme && prefersDarkMode)) {
        document.body.setAttribute('data-bs-theme', 'dark');
        themeSwitch.checked = true;
    }
    
    themeSwitch.addEventListener('change', function() {
        if (this.checked) {
            document.body.setAttribute('data-bs-theme', 'dark');
            localStorage.setItem('theme', 'dark');
        } else {
            document.body.setAttribute('data-bs-theme', 'light');
            localStorage.setItem('theme', 'light');
        }
    });
    
    if (!document.getElementById("fileInput")) return;

    // File upload functionality
    const fileInput = document.getElementById('fileInput');
    const uploadArea = document.getElementById('uploadArea');
    const browseBtn = document.getElementById('browseBtn');
    const selectedFileInfo = document.getElementById('selectedFileInfo');
    const selectedFilename = document.getElementById('selectedFilename');
    const selectedFilesize = document.getElementById('selectedFilesize');
    const removeFileBtn = document.getElementById('removeFileBtn');
    const detectBtn = document.getElementById('detectBtn');
    const newDetectionBtn = document.getElementById('newDetectionBtn');
    
    let uploadedFile = null;
    let uploadedFileName = null;
    
    // Click on browse button triggers file input
    browseBtn.addEventListener('click', function() {
        fileInput.click();
    });
    
    // Click on upload area also triggers file input
    uploadArea.addEventListener('click', function() {
        fileInput.click();
    });
    
    // File selection handler
    fileInput.addEventListener('change', function() {
        handleFileSelection(this.files[0]);
    });
    
    // Drag and drop functionality
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    ['dragenter', 'dragover'].forEach(eventName => {
        uploadArea.addEventListener(eventName, highlight, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, unhighlight, false);
    });
    
    function highlight() {
        uploadArea.classList.add('highlight-drop');
    }
    
    function unhighlight() {
        uploadArea.classList.remove('highlight-drop');
    }
    
    uploadArea.addEventListener('drop', function(e) {
        const dt = e.dataTransfer;
        const file = dt.files[0];
        handleFileSelection(file);
    });
    
    // Handle file selection
    function handleFileSelection(file) {
        if (!file) return;
        
        // Check file type
        const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/bmp'];
        if (!validTypes.includes(file.type)) {
            showAlert('Please select a valid image file (JPG, JPEG, PNG, BMP)');
            return;
        }
        
        // Check file size (max 10MB)
        if (file.size > 10 * 1024 * 1024) {
            showAlert('File size exceeds 10MB limit');
            return;
        }
        
        uploadedFile = file;
        displayFileInfo(file);
    }
    
    // Display selected file info
    function displayFileInfo(file) {
        selectedFilename.textContent = file.name;
        selectedFilesize.textContent = formatFileSize(file.size);
        uploadArea.style.display = 'none';
        selectedFileInfo.classList.remove('d-none');
    }
    
    // Format file size
    function formatFileSize(bytes) {
        if (bytes < 1024) return bytes + ' bytes';
        else if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
        else return (bytes / 1048576).toFixed(1) + ' MB';
    }
    
    // Remove selected file
    removeFileBtn.addEventListener('click', function() {
        uploadedFile = null;
        uploadedFileName = null;
        fileInput.value = '';
        selectedFileInfo.classList.add('d-none');
        uploadArea.style.display = 'block';
    });
    
    // Detect defects
    detectBtn.addEventListener('click', function() {
        if (!uploadedFile) return;
        
        // First, upload the file
        const formData = new FormData();
        formData.append('file', uploadedFile);
        
        // Show processing indicator
        document.getElementById('processingIndicator').classList.remove('d-none');
        document.getElementById('uploadSection').classList.add('d-none');
        
        // Upload the file
        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Store the uploaded filename
                uploadedFileName = data.filename;
                
                // Now run the detection
                return fetch('/detect', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ filename: data.filename })
                });
            } else {
                throw new Error(data.error || 'Upload failed');
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Display results
                displayResults(data);
            } else {
                throw new Error(data.error || 'Detection failed');
            }
        })
        .catch(error => {
            showAlert('Error: ' + error.message);
            document.getElementById('processingIndicator').classList.add('d-none');
            document.getElementById('uploadSection').classList.remove('d-none');
        });
    });
    
    // Display detection results
    function displayResults(data) {
        // Hide processing indicator
        document.getElementById('processingIndicator').classList.add('d-none');
        
        // Show results section
        const resultsSection = document.getElementById('resultsSection');
        resultsSection.classList.remove('d-none');
        
        // Set result image
        const resultImage = document.getElementById('resultImage');
        resultImage.src = data.result_path + '?t=' + new Date().getTime(); // Add timestamp to prevent caching
        
        let diagnostics = document.getElementById('inspectionDiagnostics');
        if (!diagnostics) {
            diagnostics = document.createElement('p');
            diagnostics.id = 'inspectionDiagnostics';
            diagnostics.className = 'small text-muted mt-2';
            document.getElementById('defectsCount').parentElement.after(diagnostics);
        }
        const counts = Object.entries(data.class_counts || {})
            .map(([name, count]) => `${name}: ${count}`).join(', ');
        diagnostics.textContent = `${data.diagnostic || ''} Inference: ${data.inference_ms} ms. ${counts}`;

        // Set defects count
        const defectsCount = document.getElementById('defectsCount');
        defectsCount.textContent = data.detections_count;
        
        // List defects
        const defectsList = document.getElementById('defectsList');
        defectsList.innerHTML = '';
        
        if (data.detections.length > 0) {
            data.detections.forEach(defect => {
                const defectItem = document.createElement('div');
                defectItem.className = 'defect-item';
                
                // Get color based on confidence
                let badgeClass = 'bg-danger';
                if (defect.confidence >= 0.8) badgeClass = 'bg-success';
                else if (defect.confidence >= 0.5) badgeClass = 'bg-warning';
                
                const name = document.createElement('div');
                name.className = 'defect-name';
                name.textContent = defect.class;
                const confidence = document.createElement('span');
                confidence.className = `badge ${badgeClass} confidence-badge`;
                confidence.textContent = `${(defect.confidence * 100).toFixed(0)}%`;
                defectItem.append(name, confidence);

                defectsList.appendChild(defectItem);
            });
        } else {
            defectsList.innerHTML = '<div class="text-center py-3">No visible defects detected; electrical functionality is unverified.</div>';
        }
        
        // Configure download button
        const downloadResultBtn = document.getElementById('downloadResultBtn');
        downloadResultBtn.onclick = function() {
            // Create a temporary link and trigger download
            const link = document.createElement('a');
            link.href = data.result_path;
            link.download = 'pcb_detection_result.png';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        };
    }
    
    // New detection button
    newDetectionBtn.addEventListener('click', function() {
        resetApplication();
    });
    
    // Reset application state
    function resetApplication() {
        // Reset file selection
        uploadedFile = null;
        uploadedFileName = null;
        fileInput.value = '';
        
        // Show upload section
        document.getElementById('uploadSection').classList.remove('d-none');
        selectedFileInfo.classList.add('d-none');
        uploadArea.style.display = 'block';
        
        // Hide results
        document.getElementById('resultsSection').classList.add('d-none');
        document.getElementById('processingIndicator').classList.add('d-none');
    }
    
    // Show alert message
    function showAlert(message) {
        // You can implement a proper alert UI here
        alert(message);
    }
});
