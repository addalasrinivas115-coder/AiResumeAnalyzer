/**
 * main.js
 * Client-side interactions for AI Resume & Skill Gap Analyzer.
 * Features:
 * - Drag-and-drop PDF file upload with instant feedback.
 * - File validation (format, size limits).
 * - Real-time character count for job description.
 * - One-click sample job description loader.
 * - Dynamic submit state with animated spinner.
 */

document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements - Resume Upload
    const dropzone = document.getElementById('dropzone');
    const resumeInput = document.getElementById('resumeInput');
    const dropzoneEmpty = document.getElementById('dropzoneEmpty');
    const dropzoneSelected = document.getElementById('dropzoneSelected');
    const fileNameDisplay = document.getElementById('fileNameDisplay');
    const fileSizeDisplay = document.getElementById('fileSizeDisplay');
    const btnRemoveFile = document.getElementById('btnRemoveFile');

    // DOM Elements - Job Description
    const jobDescriptionInput = document.getElementById('jobDescriptionInput');
    const charCountDisplay = document.getElementById('charCountDisplay');
    const btnClearJd = document.getElementById('btnClearJd');
    const btnFillSampleJd = document.getElementById('btnFillSampleJd');

    // DOM Elements - Form & Submit
    const analysisForm = document.getElementById('resumeAnalysisForm');
    const btnSubmitAnalysis = document.getElementById('btnSubmitAnalysis');

    // 5 Megabytes limit in bytes
    const MAX_FILE_SIZE = 5 * 1024 * 1024;

    /* -------------------------------------------------------------
       1. Resume File Handling & Drag and Drop
       ------------------------------------------------------------- */
    if (dropzone && resumeInput) {
        // Prevent default drag behaviors
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropzone.addEventListener(eventName, preventDefaults, false);
            document.body.addEventListener(eventName, preventDefaults, false);
        });

        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }

        // Highlight drop zone when item is dragged over it
        ['dragenter', 'dragover'].forEach(eventName => {
            dropzone.addEventListener(eventName, () => dropzone.classList.add('drag-active'), false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropzone.addEventListener(eventName, () => dropzone.classList.remove('drag-active'), false);
        });

        // Handle dropped files
        dropzone.addEventListener('drop', (e) => {
            const dt = e.dataTransfer;
            const files = dt.files;
            if (files && files.length > 0) {
                handleFileSelection(files[0]);
            }
        });

        // Handle file selected via standard input dialog
        resumeInput.addEventListener('change', (e) => {
            if (e.target.files && e.target.files.length > 0) {
                handleFileSelection(e.target.files[0]);
            }
        });

        // Remove file button
        if (btnRemoveFile) {
            btnRemoveFile.addEventListener('click', (e) => {
                e.stopPropagation();
                resetFileInput();
            });
        }
    }

    function handleFileSelection(file) {
        // Validate extension
        const isPdf = file.name.toLowerCase().endsWith('.pdf') || file.type === 'application/pdf';
        if (!isPdf) {
            alert('Please select a valid PDF file (.pdf). Other formats are not supported.');
            resetFileInput();
            return;
        }

        // Validate size
        if (file.size > MAX_FILE_SIZE) {
            alert('File exceeds the 5MB maximum size limit. Please upload a smaller PDF resume.');
            resetFileInput();
            return;
        }

        if (file.size === 0) {
            alert('The selected file appears to be empty (0 bytes). Please select a valid PDF resume.');
            resetFileInput();
            return;
        }

        // Assign file to input if set programmatically via drop
        if (resumeInput.files[0] !== file) {
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(file);
            resumeInput.files = dataTransfer.files;
        }

        // Update preview UI
        fileNameDisplay.textContent = file.name;
        fileSizeDisplay.textContent = formatBytes(file.size);
        dropzoneEmpty.style.display = 'none';
        dropzoneSelected.style.display = 'block';
    }

    function resetFileInput() {
        if (resumeInput) {
            resumeInput.value = '';
        }
        if (dropzoneEmpty && dropzoneSelected) {
            dropzoneEmpty.style.display = 'block';
            dropzoneSelected.style.display = 'none';
        }
    }

    function formatBytes(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }

    /* -------------------------------------------------------------
       2. Job Description Input & 1-Click Sample Loading
       ------------------------------------------------------------- */
    if (jobDescriptionInput) {
        function updateCharCount() {
            const length = jobDescriptionInput.value.length;
            if (charCountDisplay) {
                charCountDisplay.textContent = `${length.toLocaleString()} characters`;
            }
            if (btnClearJd) {
                btnClearJd.style.display = length > 0 ? 'inline-block' : 'none';
            }
        }

        jobDescriptionInput.addEventListener('input', updateCharCount);
        updateCharCount(); // Initial check

        if (btnClearJd) {
            btnClearJd.addEventListener('click', () => {
                jobDescriptionInput.value = '';
                updateCharCount();
                jobDescriptionInput.focus();
            });
        }
    }

    // Auto-fill sample job description
    if (btnFillSampleJd && jobDescriptionInput) {
        btnFillSampleJd.addEventListener('click', async () => {
            const originalText = btnFillSampleJd.innerHTML;
            btnFillSampleJd.disabled = true;
            btnFillSampleJd.innerHTML = `<span>Loading sample...</span>`;

            try {
                const response = await fetch('/api/sample-job-description');
                if (!response.ok) {
                    throw new Error(`Server returned ${response.status}`);
                }
                const data = await response.json();
                if (data.status === 'success' && data.content) {
                    jobDescriptionInput.value = data.content;
                    const event = new Event('input', { bubbles: true });
                    jobDescriptionInput.dispatchEvent(event);
                    btnFillSampleJd.innerHTML = `<span>&check; Loaded Sample!</span>`;
                    setTimeout(() => {
                        btnFillSampleJd.innerHTML = originalText;
                        btnFillSampleJd.disabled = false;
                    }, 1800);
                } else {
                    throw new Error(data.message || 'Unknown response');
                }
            } catch (err) {
                console.error('Failed to load sample job description:', err);
                alert('Could not load sample job description from server.');
                btnFillSampleJd.innerHTML = originalText;
                btnFillSampleJd.disabled = false;
            }
        });
    }

    /* -------------------------------------------------------------
       3. Form Submission & Client-side Validation
       ------------------------------------------------------------- */
    if (analysisForm && btnSubmitAnalysis) {
        analysisForm.addEventListener('submit', (e) => {
            // Check file
            if (!resumeInput.files || resumeInput.files.length === 0) {
                e.preventDefault();
                alert('Please upload a PDF resume before analyzing.');
                dropzone.scrollIntoView({ behavior: 'smooth' });
                return;
            }

            // Check JD
            const jd = (jobDescriptionInput.value || '').trim();
            if (!jd) {
                e.preventDefault();
                alert('Please enter or paste a job description.');
                jobDescriptionInput.focus();
                return;
            }

            if (jd.length < 30) {
                e.preventDefault();
                alert('The job description is too short (minimum 30 characters). Please provide a more detailed job posting.');
                jobDescriptionInput.focus();
                return;
            }

            // Set loading state on button
            btnSubmitAnalysis.disabled = true;
            const normalSpan = btnSubmitAnalysis.querySelector('.btn-content-normal');
            const loadingSpan = btnSubmitAnalysis.querySelector('.btn-content-loading');
            if (normalSpan && loadingSpan) {
                normalSpan.style.display = 'none';
                loadingSpan.style.display = 'inline-flex';
            }
        });
    }
});
