document.addEventListener('DOMContentLoaded', (event) => {
    // --- DARK MODE LOGIC (Universal) ---
    const themeSwitch = document.querySelector('.theme-switch__checkbox');

    function applyTheme(theme) {
        if (theme === 'dark') {
            document.documentElement.classList.add('dark-mode');
            if (themeSwitch) themeSwitch.checked = true;
        } else {
            document.documentElement.classList.remove('dark-mode');
            if (themeSwitch) themeSwitch.checked = false;
        }
    }

    if (themeSwitch) {
        themeSwitch.addEventListener('change', function() {
            if (this.checked) {
                localStorage.setItem('theme', 'dark');
                applyTheme('dark');
            } else {
                localStorage.setItem('theme', 'light');
                applyTheme('light');
            }
        });
    }

    // Apply saved theme on initial load
    const savedTheme = localStorage.getItem('theme') || 'light';
    applyTheme(savedTheme);
    // --- END DARK MODE LOGIC ---


    // --- INDEX.HTML SPECIFIC LOGIC ---
    // This ensures the following code only runs on the main page
    const uploadForm = document.getElementById('uploadForm');
    if (uploadForm) {
        const fileInput = document.getElementById('file-input');
        const fileNameSpan = document.getElementById('selectedFileName');
        const imagePreview = document.getElementById('imagePreview');
        const customFileUpload = document.getElementById('customFileUpload');
        const loadingOverlay = document.getElementById('loadingOverlay');
        const textSearchInput = document.getElementById('textSearchInput');
        const ocrTextContent = document.getElementById('ocrTextContent');
        const resultsSection = document.querySelector('.results');
        const processingTimerElement = document.getElementById('processingTimer');

        let originalOcrText = ocrTextContent ? ocrTextContent.textContent : '';
        let processingStartTime;
        let processingTimerInterval;

        function showLoading() {
            loadingOverlay.classList.add('active');
            processingStartTime = new Date().getTime();
            processingTimerElement.textContent = '0 seconds';
            processingTimerInterval = setInterval(updateProcessingTimer, 1000);
        }

        function hideLoading() {
            loadingOverlay.classList.remove('active');
            clearInterval(processingTimerInterval);
            processingTimerElement.textContent = '';
        }

        function updateProcessingTimer() {
            const currentTime = new Date().getTime();
            const elapsedMilliseconds = currentTime - processingStartTime;
            const elapsedSeconds = Math.floor(elapsedMilliseconds / 1000);
            processingTimerElement.textContent = `${elapsedSeconds} seconds`;
        }

        function clearAnalysisResults() {
            const hr = document.querySelector('.results-divider');
            if (hr) {
                hr.remove();
            }
            if (resultsSection) {
                resultsSection.innerHTML = '';
            }
            resetFileInput();
        }

        function handleFile(file) {
            if (file && file.type.startsWith('image/')) {
                clearAnalysisResults();
                const reader = new FileReader();
                fileNameSpan.textContent = file.name;
                reader.onload = function(e) {
                    imagePreview.src = e.target.result;
                    imagePreview.style.display = 'block';
                    customFileUpload.style.display = 'none';
                };
                reader.readAsDataURL(file);
                const dataTransfer = new DataTransfer();
                dataTransfer.items.add(file);
                fileInput.files = dataTransfer.files;
            } else {
                resetFileInput();
            }
        }

        function resetFileInput() {
            fileInput.value = '';
            fileNameSpan.textContent = '';
            imagePreview.src = '#';
            imagePreview.style.display = 'none';
            customFileUpload.style.display = 'flex';
            if (textSearchInput) textSearchInput.value = '';
            if (ocrTextContent) ocrTextContent.innerHTML = originalOcrText;
        }

        fileInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                handleFile(this.files[0]);
            } else {
                resetFileInput();
            }
        });

        customFileUpload.addEventListener('dragover', (e) => {
            e.preventDefault();
            customFileUpload.classList.add('drag-over');
        });
        customFileUpload.addEventListener('dragleave', () => {
            customFileUpload.classList.remove('drag-over');
        });
        customFileUpload.addEventListener('drop', (e) => {
            e.preventDefault();
            customFileUpload.classList.remove('drag-over');
            if (e.dataTransfer.files.length > 0) {
                handleFile(e.dataTransfer.files[0]);
            }
        });

        imagePreview.addEventListener('click', () => {
            fileInput.click();
        });
        imagePreview.addEventListener('dragover', (e) => {
            e.preventDefault();
            imagePreview.classList.add('drag-over');
        });
        imagePreview.addEventListener('dragleave', () => {
            imagePreview.classList.remove('drag-over');
        });
        imagePreview.addEventListener('drop', (e) => {
            e.preventDefault();
            imagePreview.classList.remove('drag-over');
            if (e.dataTransfer.files.length > 0) {
                handleFile(e.dataTransfer.files[0]);
            }
        });

        uploadForm.addEventListener('submit', (e) => {
            if (fileInput.files && fileInput.files.length > 0) {
                showLoading();
            } else {
                e.preventDefault();
                alert('Please select an image to upload!');
            }
        });

        if (resultsSection && ocrTextContent) {
            originalOcrText = ocrTextContent.textContent;
            hideLoading();
        } else {
            hideLoading();
        }

        if (fileInput.files && fileInput.files.length > 0) {
            // Handle pre-selected file
        } else {
            resetFileInput();
        }

        if (textSearchInput && ocrTextContent) {
            textSearchInput.addEventListener('input', function() {
                const searchTerm = this.value.trim();
                const textToSearch = originalOcrText;
                ocrTextContent.innerHTML = textToSearch;
                if (searchTerm.length > 0) {
                    const regex = new RegExp(searchTerm, 'gi');
                    let newHtml = textToSearch.replace(regex, (match) => {
                        return `<span class="highlight">${match}</span>`;
                    });
                    ocrTextContent.innerHTML = newHtml;
                }
            });
        }
    }
});