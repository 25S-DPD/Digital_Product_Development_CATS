/*
Makes backend API call to rasa chatbot and display output to chatbot frontend
Enhanced with JWT token handling from URL parameters and automatic file upload
*/

function init() {

    //---------------------------- Including Jquery ------------------------------

    var script = document.createElement('script');
    script.src = 'https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js';
    script.type = 'text/javascript';
    document.getElementsByTagName('head')[0].appendChild(script);

    //--------------------------- Important Variables----------------------------
    botLogoPath = "./imgs/bot-logo.png"

    //--------------------------- Extract JWT Token from URL -----------------------
    jwtToken = extractTokenFromURL();
    if (!jwtToken) {
        console.warn("No JWT token found in URL parameters");
        // Optionally show an error message to the user
        // showAuthenticationError();
    } else {
        console.log("JWT token extracted and ready for use");
    }

    //--------------------------- Chatbot Frontend -------------------------------
    const chatContainer = document.getElementById("chat-container");

    template = ` <button class='chat-btn'><img src = "./icons/comment.png" class = "icon" ></button>

    <div class='chat-popup'>
    
		<div class='chat-header'>
			<div class='chatbot-img'>
				<img src='${botLogoPath}' alt='Chat Bot image' class='bot-img'> 
			</div>
			<h3 class='bot-title'>Covid Bot</h3>
			<button class = "expand-chat-window" ><img src="./icons/open_fullscreen.png" class="icon" ></button>
		</div>

		<div class='chat-area'>
            <div class='bot-msg'>
                <img class='bot-img' src ='${botLogoPath}' />
				<span class='msg'>Are you ready to start your medical history assessment? Make sure to have all your medicines and exams with you.</span>
			</div>
			<div class='bot-msg'>
				<img class='bot-img' src ='${botLogoPath}' />
				<div class='response-btns ready-buttons' style='flex-direction: column; gap: 10px;'>
					<button class='btn-primary' onclick='startChatSession()' value='yes'>Yes, I'm ready</button>
					<button class='btn-primary' onclick='declineStart()' value='no'>Not now</button>
				</div>
			</div>

            <!-- File upload input (hidden) -->
            <input type="file" id="fileUpload" multiple accept="image/*,.pdf,.doc,.docx" style="display: none;">

		</div>

		<div class='chat-input-area'>
			<input type='text' autofocus class='chat-input' onkeypress='return givenUserInput(event)' placeholder='Type a message ...' autocomplete='off'>
			<button class='chat-submit'><i class='material-icons'>send</i></button>
		</div>

	</div>`


    chatContainer.innerHTML = template;

    //--------------------------- Important Variables----------------------------
    var inactiveMessage = "Server is down, Please contact the developer to activate it"


    chatPopup = document.querySelector(".chat-popup")
    chatBtn = document.querySelector(".chat-btn")
    chatSubmit = document.querySelector(".chat-submit")
    chatHeader = document.querySelector(".chat-header")
    chatArea = document.querySelector(".chat-area")
    chatInput = document.querySelector(".chat-input")
    expandWindow = document.querySelector(".expand-chat-window")
    fileUpload = document.querySelector("#fileUpload")
    root = document.documentElement;
    chatPopup.style.display = "none"
    //var host = "http://localhost:5005/webhooks/rest/webhook";
    var host = "http://91.99.232.111:5005/webhooks/rest/webhook"

    // File upload event listener
    fileUpload.addEventListener('change', handleFileUpload);

    //------------------------ ChatBot Toggler -------------------------

    chatBtn.addEventListener("click", () => {

        mobileDevice = !detectMob()
        if (chatPopup.style.display == "none" && mobileDevice) {
            chatPopup.style.display = "flex"
            chatInput.focus();
            chatBtn.innerHTML = `<img src = "./icons/close.png" class = "icon" >`
            
            // JWT token is now available in metadata for any future messages
            // No automatic session start message sent
        } else if (mobileDevice) {
            chatPopup.style.display = "none"
            chatBtn.innerHTML = `<img src = "./icons/comment.png" class = "icon" >`
        } else {
            mobileView()
        }
    })

    chatSubmit.addEventListener("click", () => {
        let userResponse = chatInput.value.trim();
        if (userResponse !== "" && chatStarted) {
            setUserResponse();
            send(userResponse)
        } else if (!chatStarted && userResponse !== "") {
            // Clear input if chat hasn't started yet
            chatInput.value = "";
        }
    })

    expandWindow.addEventListener("click", (e) => {
        // console.log(expandWindow.innerHTML)
        if (expandWindow.innerHTML == '<img src="./icons/open_fullscreen.png" class="icon">') {
            expandWindow.innerHTML = `<img src = "./icons/close_fullscreen.png" class = 'icon'>`
            root.style.setProperty('--chat-window-height', 80 + "%");
            root.style.setProperty('--chat-window-total-width', 85 + "%");
        } else if (expandWindow.innerHTML == '<img src="./icons/close.png" class="icon">') {
            chatPopup.style.display = "none"
            chatBtn.style.display = "block"
        } else {
            expandWindow.innerHTML = `<img src = "./icons/open_fullscreen.png" class = "icon" >`
            root.style.setProperty('--chat-window-height', 500 + "px");
            root.style.setProperty('--chat-window-total-width', 380 + "px");
        }

    })
}

// Function to extract JWT token from URL parameters
function extractTokenFromURL() {
    const urlParams = new URLSearchParams(window.location.search);
    
    // Try different parameter names that might contain the token
    const tokenParams = ['token', 'jwt', 'auth', 'authorization', 'access_token'];
    
    for (const param of tokenParams) {
        const token = urlParams.get(param);
        if (token) {
            console.log(`JWT token found in URL parameter: ${param}`);
            return token;
        }
    }
    
    // Also check hash parameters (after #)
    const hash = window.location.hash;
    if (hash) {
        const hashParams = new URLSearchParams(hash.substring(1));
        for (const param of tokenParams) {
            const token = hashParams.get(param);
            if (token) {
                console.log(`JWT token found in URL hash parameter: ${param}`);
                return token;
            }
        }
    }
    
    return null;
}

// Function to extract patient ID from JWT token
function extractPatientIdFromToken() {
    if (!jwtToken) return null;
    
    try {
        // Decode JWT token (assuming it's a standard JWT)
        const payload = JSON.parse(atob(jwtToken.split('.')[1]));
        return payload.patient_id || payload.sub || payload.userId;
    } catch (error) {
        console.error('Error decoding JWT token:', error);
        return null;
    }
}

// Function to extract patient ID from URL parameters
function extractPatientIdFromURL() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('patient_id') || urlParams.get('patientId');
}

// Function to display uploading message
function displayUploadingMessage(message) {
    const uploadingMsg = `<div class='bot-msg'><img class='bot-img' src ='${botLogoPath}' /><span class='msg' style='color: #0066cc;'>${message}</span></div>`;
    chatArea.innerHTML += uploadingMsg;
    scrollToBottomOfResults();
}

// Function to display success message
function displaySuccessMessage(message) {
    const successMsg = `<div class='bot-msg'><img class='bot-img' src ='${botLogoPath}' /><span class='msg' style='color: green;'>${message}</span></div>`;
    chatArea.innerHTML += successMsg;
    scrollToBottomOfResults();
}

// Function to display error message
function displayErrorMessage(message) {
    const errorMsg = `<div class='bot-msg'><img class='bot-img' src ='${botLogoPath}' /><span class='msg' style='color: red;'>${message}</span></div>`;
    chatArea.innerHTML += errorMsg;
    scrollToBottomOfResults();
}

// Function to show authentication error (kept for potential future use)
function showAuthenticationError() {
    const errorMsg = "Authentication required. Please access this chat through the proper link.";
    var errorResponse = `<div class='bot-msg'><img class='bot-img' src ='${botLogoPath}' /><span class='msg' style='color: red;'> ${errorMsg} </span></div>`;
    chatArea.innerHTML += errorResponse;
    chatInput.disabled = true;
}

// end of init function
var passwordInput = false;
var jwtToken = null; // Global variable to store JWT token
var chatStarted = false; // Flag to track if chat session has started

// Function to start the chat session
function startChatSession() {
    // Hide the ready buttons
    const readyButtons = document.querySelector('.ready-buttons');
    if (readyButtons) {
        readyButtons.style.display = 'none';
    }
    
    // Show user's choice
    let temp = `<div class="user-msg"><span class="msg">Yes, I'm ready</span></div>`;
    chatArea.innerHTML += temp;
    scrollToBottomOfResults();
    
    // Set flag and send hello message to trigger the greet intent
    chatStarted = true;
    send("hello");
}

// Function to handle decline
function declineStart() {
    // Hide the ready buttons
    const readyButtons = document.querySelector('.ready-buttons');
    if (readyButtons) {
        readyButtons.style.display = 'none';
    }
    
    // Show user's choice
    let temp = `<div class="user-msg"><span class="msg">Not now</span></div>`;
    chatArea.innerHTML += temp;
    
    // Show bot response
    var BotResponse = `<div class='bot-msg'><img class='bot-img' src ='${botLogoPath}' /><span class='msg'>No problem! Click "Yes, I'm ready" when you're ready to begin your medical history assessment.</span></div>`;
    chatArea.innerHTML += BotResponse;
    scrollToBottomOfResults();
    
    // Re-show the ready buttons after a brief delay
    setTimeout(() => {
        var newButtons = `<div class='bot-msg'><img class='bot-img' src ='${botLogoPath}' /><div class='response-btns ready-buttons' style='flex-direction: column; gap: 10px;'>
            <button class='btn-primary' onclick='startChatSession()' value='yes'>Yes, I'm ready</button>
            <button class='btn-primary' onclick='declineStart()' value='no'>Not now</button>
        </div></div>`;
        chatArea.innerHTML += newButtons;
        scrollToBottomOfResults();
    }, 1000);
}

// Enhanced userResponseBtn function to handle file uploads
function userResponseBtn(e) {
    // Check if user clicked upload button
    if (e.value === 'upload_files' || e.value === 'upload_more_files') {
        triggerFileUpload();
    } else {
        send(e.value);
    }
}

// Function to trigger file upload dialog
function triggerFileUpload() {
    fileUpload.click();
}

// Enhanced file upload function that automatically sends files to your API
function handleFileUpload(event) {
    const files = event.target.files;
    if (files.length > 0) {
        let fileNames = [];
        let fileDetails = [];
        
        // Extract patient_id from JWT token or URL parameters
        const patientId = extractPatientIdFromToken() || extractPatientIdFromURL();
        
        if (!patientId) {
            console.error("Patient ID not found");
            displayErrorMessage("Unable to identify patient. Please refresh and try again.");
            return;
        }
        
        // Process each file
        for (let i = 0; i < files.length; i++) {
            fileNames.push(files[i].name);
            fileDetails.push({
                name: files[i].name,
                size: formatFileSize(files[i].size),
                type: files[i].type
            });
            
            // Automatically upload each file to the server
            uploadFileToServer(files[i], patientId);
        }
        
        // Display uploaded files in chat
        displayUploadedFiles(fileDetails);
        
        // Send file information to Rasa (this should trigger the "upload more?" question)
        const fileMessage = `Uploaded files: ${fileNames.join(', ')}`;
        send(fileMessage);
        
        // Reset file input
        event.target.value = '';
    }
}

// Function to automatically upload file to your API endpoint
async function uploadFileToServer(file, patientId) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('patient_id', patientId);
    
    // Show uploading status
    displayUploadingMessage(`Uploading "${file.name}"...`);
    
    try {
        const response = await fetch('https://redcore-latest.onrender.com/upload-public', {
            method: 'POST',
            body: formData,
            headers: {
                // Add JWT token if needed for authentication
                ...(jwtToken && { 'Authorization': `Bearer ${jwtToken}` })
            }
        });
        
        if (response.ok) {
            const result = await response.json();
            console.log('File uploaded successfully:', result);
            // Success message removed to prevent interference with chat flow
            // displaySuccessMessage(`✅ "${file.name}" uploaded successfully`);
        } else {
            const error = await response.text();
            console.error('File upload failed:', error);
            displayErrorMessage(`❌ Failed to upload "${file.name}"`);
        }
    } catch (error) {
        console.error('Upload error:', error);
        displayErrorMessage(`❌ Error uploading "${file.name}"`);
    }
}
// Function to display uploaded files in chat
function displayUploadedFiles(fileDetails) {
    let fileListHTML = '<div class="uploaded-files"><strong>Uploaded Files:</strong><ul>';
    
    fileDetails.forEach(file => {
        fileListHTML += `<li>${file.name} (${file.size})</li>`;
    });
    
    fileListHTML += '</ul></div>';
    
    let temp = `<div class="user-msg"><span class="msg">${fileListHTML}</span></div>`;
    chatArea.innerHTML += temp;
    scrollToBottomOfResults();
}

// Function to format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// to submit user input when he presses enter
function givenUserInput(e) {
    if (e.keyCode == 13) {
        let userResponse = chatInput.value.trim();
        if (userResponse !== "" && chatStarted) {
            setUserResponse()
            send(userResponse)
        } else if (!chatStarted) {
            // Prevent typing before clicking "Yes, I'm ready"
            chatInput.value = "";
            // Optional: Show a message reminding user to click the button first
        }
    }
}

// to display user message on UI
function setUserResponse() {
    let userInput = chatInput.value;
    if (passwordInput) {
        userInput = "******"
    }
    if (userInput) {
        let temp = `<div class="user-msg"><span class = "msg">${userInput}</span></div>`
        chatArea.innerHTML += temp;
        chatInput.value = ""
    } else {
        chatInput.disabled = false;
    }
    scrollToBottomOfResults();
}

function scrollToBottomOfResults() {
    chatArea.scrollTop = chatArea.scrollHeight;
}

/***************************************************************
Frontend Part Completed
****************************************************************/

// Enhanced send function with JWT token in metadata
function send(message) {
    // Disable input during initial ready check
    if (!chatStarted && message !== "hello") {
        return;
    }
    
    chatInput.type = "text"
    passwordInput = false;
    chatInput.focus();
    console.log("User Message:", message)
    
    // Check if this is a file upload message
    const isFileUpload = message.includes("Uploaded files:");
    
    // Prepare request data with JWT token in metadata
    const requestData = {
        "message": message,
        "sender": "User"
    };
    
    // Add metadata to indicate file upload context
    if (isFileUpload) {
        requestData.metadata = {
            "message_type": "file_upload",
            ...(jwtToken && { "jwt_token": jwtToken, "authorization": `Bearer ${jwtToken}` })
        };
    } else if (jwtToken) {
        requestData.metadata = {
            "jwt_token": jwtToken,
            "authorization": `Bearer ${jwtToken}`
        };
    }
    
    if (jwtToken) {
        console.log("Sending message with JWT token in metadata");
    }
    
    $.ajax({
        url: host,
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(requestData),
        success: function(data, textStatus) {
            if (data != null) {
                setBotResponse(data);
            }
            console.log("Rasa Response: ", data, "\n Status:", textStatus)
        },
        error: function(errorMessage) {
            setBotResponse("");
            console.log('Error' + errorMessage);
        }
    });
    chatInput.focus();
}
//------------------------------------ Set bot response -------------------------------------
function setBotResponse(val) {
    setTimeout(function() {
        if (val.length < 1) {
            //if there is no response from Rasa
            // msg = 'I couldn\'t get that. Let\' try something else!';
            msg = inactiveMessage;

            var BotResponse = `<div class='bot-msg'><img class='bot-img' src ='${botLogoPath}' /><span class='msg'> ${msg} </span></div>`;
            $(BotResponse).appendTo('.chat-area').hide().fadeIn(1000);
            scrollToBottomOfResults();
            chatInput.focus();

        } else {
            //if we get response from Rasa
            for (i = 0; i < val.length; i++) {
                //check if there is text message
                if (val[i].hasOwnProperty("text")) {
                    const botMsg = val[i].text;
                    if (botMsg.includes("password")) {
                        chatInput.type = "password";
                        passwordInput = true;
                    }
                    var BotResponse = `<div class='bot-msg'><img class='bot-img' src ='${botLogoPath}' /><span class='msg'>${val[i].text}</span></div>`;
                    $(BotResponse).appendTo('.chat-area').hide().fadeIn(1000);
                }

                //check if there is image
                if (val[i].hasOwnProperty("image")) {
                    var BotResponse = "<div class='bot-msg'>" + "<img class='bot-img' src ='${botLogoPath}' />"
                    '<img class="msg-image" src="' + val[i].image + '">' +
                        '</div>'
                    $(BotResponse).appendTo('.chat-area').hide().fadeIn(1000);
                }

                //check if there are buttons
                if (val[i].hasOwnProperty("buttons")) {
                    var BotResponse = `<div class='bot-msg'><img class='bot-img' src ='${botLogoPath}' /><div class='response-btns'>`

                    buttonsArray = val[i].buttons;
                    buttonsArray.forEach(btn => {
                        BotResponse += `<button class='btn-primary' onclick= 'userResponseBtn(this)' value='${btn.payload}'>${btn.title}</button>`
                    })

                    BotResponse += "</div></div>"

                    $(BotResponse).appendTo('.chat-area').hide().fadeIn(1000);
                    chatInput.disabled = true;
                }

            }
            scrollToBottomOfResults();
            chatInput.disabled = false;
            chatInput.focus();
        }

    }, 500);
}

function mobileView() {
    $('.chat-popup').width($(window).width());

    if (chatPopup.style.display == "none") {
        chatPopup.style.display = "flex"
            // chatInput.focus();
        chatBtn.style.display = "none"
        chatPopup.style.bottom = "0"
        chatPopup.style.right = "0"
            // chatPopup.style.transition = "none"
        expandWindow.innerHTML = `<img src = "./icons/close.png" class = "icon" >`
        
        // JWT token is available in metadata for any future messages
        // No automatic session start message sent for mobile either
    }
}

function detectMob() {
    return ((window.innerHeight <= 800) && (window.innerWidth <= 600));
}

function chatbotTheme(theme) {
    const gradientHeader = document.querySelector(".chat-header");
    const orange = {
        color: "#FBAB7E",
        background: "linear-gradient(19deg, #FBAB7E 0%, #F7CE68 100%)"
    }

    const purple = {
        color: "#B721FF",
        background: "linear-gradient(19deg, #21D4FD 0%, #B721FF 100%)"
    }

    if (theme === "orange") {
        root.style.setProperty('--chat-window-color-theme', orange.color);
        gradientHeader.style.backgroundImage = orange.background;
        chatSubmit.style.backgroundColor = orange.color;
    } else if (theme === "purple") {
        root.style.setProperty('--chat-window-color-theme', purple.color);
        gradientHeader.style.backgroundImage = purple.background;
        chatSubmit.style.backgroundColor = purple.color;
    }
}

function createChatBot(hostURL, botLogo, title, welcomeMessage, inactiveMsg, theme = "blue") {

    host = hostURL;
    botLogoPath = botLogo;
    inactiveMessage = inactiveMsg;
    init()
    const msg = document.querySelector(".msg");
    msg.innerText = welcomeMessage;

    const botTitle = document.querySelector(".bot-title");
    botTitle.innerText = title;

    chatbotTheme(theme)
}