export class SpeechToText {
    #micButtonElement;
    #outputElement;
    #clearButtonElement;
    #copyButtonElement;
    #speechRecognition;
    #serverCheckInterval;
    #messageQueue = [];
    #isServerConnected = false;

    _isListening;
    get isListening() {
        return this._isListening;
    }

    set isListening(value) {
        this._isListening = value;

        if (value) {
            this.#micButtonElement.classList.add('listening');
        } else {
            this.#micButtonElement.classList.remove('listening');
        }
    }
    
    #_activeText;
    get activeText() {
        return this.#_activeText;
    }

    set activeText(value) {
        this.#_activeText = value;
        this.#activeTextElement.innerText = value;
    }

    #activeTextElement;
    #outputTextElement;

    #_outputText = '';
    get outputText() {
        return this.#_outputText;
    }
    
    set outputText(value) {
        this.#_outputText = value;
        this.#outputTextElement.innerHTML = value;
    }

    /**
     * 
     * @param {{
     *      micElementSelector: string;
     *      outputElementSelector: string;
     *      clearElementSelector: string;
     *      copyElementSelector: string;
     * }} options 
     */
    constructor(options) {
        if (this.#optionsNullCheck(options)) {
            console.error('Closing app...');
            return;
        }

        const {
            micElementSelector,
            outputElementSelector,
            clearElementSelector,
            copyElementSelector,
        } = options;

        this.#micButtonElement = document.querySelector(micElementSelector);
        this.#outputElement = document.querySelector(outputElementSelector);
        this.#clearButtonElement = document.querySelector(clearElementSelector);
        this.#copyButtonElement = document.querySelector(copyElementSelector);

        this.#outputElement.innerHTML = `<span class="output"></span><span class="active-text"></span>`;
        
        this.#activeTextElement = this.#outputElement.querySelector('.active-text');
        this.#outputTextElement = this.#outputElement.querySelector('.output');
        
        this.isListening = false;
        this.#addEventListeners();
        this.#enableSpeechRecognition();
        
        // Start server connection check
        this.#checkServerConnection();
    }

    async #checkServerConnection() {
        const checkServer = async () => {
            try {
                const response = await fetch('http://localhost:5000/status');
                if (response.ok) {
                    if (!this.#isServerConnected) {
                        console.log('Server connected! Processing queued messages...');
                    }
                    this.#isServerConnected = true;
                    
                    // Process any queued messages
                    while (this.#messageQueue.length > 0) {
                        const text = this.#messageQueue.shift();
                        await this.#sendToChatbot(text);
                    }
                } else {
                    if (this.#isServerConnected) {
                        console.log('Server connection lost. Messages will be queued.');
                    }
                    this.#isServerConnected = false;
                }
            } catch (error) {
                if (this.#isServerConnected) {
                    console.log('Server connection lost. Messages will be queued.');
                }
                this.#isServerConnected = false;
                console.log('Waiting for server to come online...');
            }
        };

        // Check immediately
        await checkServer();
        
        // Then check every 5 seconds
        this.#serverCheckInterval = setInterval(checkServer, 5000);
    }

    async #sendToChatbot(text) {
        try {
            if (!this.#isServerConnected) {
                console.log('Server not connected. Queueing message:', text);
                this.#messageQueue.push(text);
                this.#showNotification('Message queued. Waiting for server...');
                return;
            }

            console.log('Sending to chatbot:', text);
            const response = await fetch('http://localhost:5000/chatbot', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ user_input: text })
            });
            
            const data = await response.json();
            console.log('Server response:', data);
            
            if (response.ok) {
                this.#showNotification('Message sent successfully!');
            } else {
                throw new Error(data.error || 'Server error');
            }
        } catch (error) {
            console.error('Error sending to chatbot:', error);
            this.#messageQueue.push(text);
            this.#isServerConnected = false;
            this.#showNotification('Error sending message. Will retry...');
        }
    }

    #extractTranscript(event) {
        return event.results[0][0].transcript;
    }

    #enableSpeechRecognition() {
        window.SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        this.#speechRecognition = new SpeechRecognition();
        this.#speechRecognition.interimResults = true;
        
        this.#speechRecognition.addEventListener('result', event => {
            console.log(event.results);
            const transcript = this.#extractTranscript(event);
            this.activeText = ' ' + transcript;
        });

        this.#speechRecognition.addEventListener('end', this.#onRecognitionEnd.bind(this));
    }

    #onRecognitionEnd() {
        this.#updateOutputText();
        if (this.outputText.trim()) {
            this.#sendToChatbot(this.outputText.trim());
        }
        if (this.isListening) {
            this.startRecognition();
        }
    }

    #updateOutputText() {
        if (!this.activeText) {
            return;
        }

        this.outputText += ' ' + this.activeText;
        this.activeText = '';
    }

    #optionsNullCheck(options) {
        const nullSelectors = [
            'micElementSelector',
            'outputElementSelector',
            'clearElementSelector',
            'copyElementSelector'
        ].filter(selector => !options[selector]);

        if (nullSelectors.length) {
            console.error(`Please provide the following selectors: ${nullSelectors.join(', ')}`);
            return true;
        }

        return false;
    }

    #addEventListeners() {
        this.#micButtonElement.addEventListener('click', this.toggleListen.bind(this));
        this.#clearButtonElement.addEventListener('click', this.#clearEverything.bind(this));
        this.#copyButtonElement.addEventListener('click', this.#copyOutput.bind(this));
    }

    toggleListen() {
        if (this.isListening) {
            this.stopRecognition();
        } else {
            this.startRecognition();
        }
    }

    startRecognition() {
        this.isListening = true;
        this.#speechRecognition.start();
    }

    stopRecognition() {
        this.isListening = false;
        this.#speechRecognition.stop();
    }

    #clearEverything() {
        this.activeText = '';
        this.outputText = '';
    }
    
    #copyOutput() {
        navigator.clipboard.writeText(this.outputText);
        this.#showNotification('Copied to clipboard!');
    }

    #showNotification(msg) {
        const notificationElement = document.createElement('div');
        notificationElement.className = 'alert';
        notificationElement.innerText = msg;

        document.body.append(notificationElement);

        setTimeout(() => {
            notificationElement.parentElement.removeChild(notificationElement);
        }, 3000);
    }

    // Cleanup method to clear the interval when the instance is destroyed
    destroy() {
        if (this.#serverCheckInterval) {
            clearInterval(this.#serverCheckInterval);
        }
        this.stopRecognition();
    }
}