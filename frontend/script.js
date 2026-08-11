document.addEventListener('DOMContentLoaded', () => {
    const generatePlanBtn = document.querySelector('.generate-plan-btn');
    const generateVideoBtn = document.querySelector('.storyboard-actions .btn-primary');
    const promptInput = document.getElementById('prompt-input');
    
    let currentPlan = null;

    // Generate Plan
    generatePlanBtn.addEventListener('click', async () => {
        const prompt = promptInput.value;
        if (!prompt) return;

        const originalText = generatePlanBtn.innerHTML;
        generatePlanBtn.innerHTML = '<i class="ph ph-spinner-gap spinner"></i> Generating Plan...';
        
        try {
            const response = await fetch('/api/generate_plan', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt: prompt, duration: 15, provider: 'gemini' })
            });
            const data = await response.json();
            
            if (data.status === 'success') {
                currentPlan = data.plan;
                generatePlanBtn.innerHTML = '<i class="ph-fill ph-check-circle"></i> Plan Generated';
                generatePlanBtn.style.background = 'var(--success)';
                generatePlanBtn.style.boxShadow = '0 0 15px rgba(16, 185, 129, 0.4)';
                
                // Here we would typically update the UI with the plan details
                console.log("Plan generated:", currentPlan);
            } else {
                throw new Error(data.message);
            }
        } catch (error) {
            console.error(error);
            generatePlanBtn.innerHTML = '<i class="ph-fill ph-x-circle"></i> Error';
            generatePlanBtn.style.background = '#ef4444';
        }
        
        setTimeout(() => {
            generatePlanBtn.innerHTML = originalText;
            generatePlanBtn.style.background = '';
            generatePlanBtn.style.boxShadow = '';
        }, 3000);
    });

    // Generate Video
    if(generateVideoBtn) {
        generateVideoBtn.addEventListener('click', async () => {
            if (!currentPlan) {
                alert("Please generate a plan first!");
                return;
            }

            const originalText = generateVideoBtn.innerHTML;
            generateVideoBtn.innerHTML = '<i class="ph ph-spinner-gap spinner"></i> Starting Job...';
            
            try {
                // 1. Start the job
                const response = await fetch('/api/generate_video', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ plan: currentPlan })
                });
                const data = await response.json();
                
                if (data.status === 'accepted') {
                    const jobId = data.job_id;
                    
                    // 2. Poll for status
                    const pollInterval = setInterval(async () => {
                        const statusRes = await fetch(`/api/job/${jobId}`);
                        const statusData = await statusRes.json();
                        
                        if (statusData.status === 'processing') {
                            generateVideoBtn.innerHTML = `<i class="ph ph-spinner-gap spinner"></i> ${statusData.message || 'Rendering...'}`;
                        } else if (statusData.status === 'success') {
                            clearInterval(pollInterval);
                            generateVideoBtn.innerHTML = '<i class="ph-fill ph-check-circle"></i> Video Ready!';
                            generateVideoBtn.style.background = 'var(--success)';
                            console.log("Video URL:", statusData.video_url);
                            
                            // Optional: open it in a new tab for now
                            window.open(statusData.video_url, '_blank');
                            
                            setTimeout(() => {
                                generateVideoBtn.innerHTML = originalText;
                                generateVideoBtn.style.background = '';
                            }, 5000);
                        } else if (statusData.status === 'error') {
                            clearInterval(pollInterval);
                            throw new Error(statusData.message);
                        }
                    }, 3000);
                    
                } else {
                    throw new Error(data.message);
                }
            } catch (error) {
                console.error(error);
                generateVideoBtn.innerHTML = '<i class="ph-fill ph-x-circle"></i> Error';
                generateVideoBtn.style.background = '#ef4444';
                setTimeout(() => {
                    generateVideoBtn.innerHTML = originalText;
                    generateVideoBtn.style.background = '';
                }, 3000);
            }
        });
    }
});
