let speech = new SpeechSynthesisUtterance() //This line creates a new instance of the SpeechSynthesisUtterance object, which represents the text that will be spoken.

let voices = []; //This line initializes an empty array called voices where the available voices will be stored.
let voiceSelect = document.querySelector("select"); //This line selects the <select> element from the HTML document, presumably used for selecting different voices.


window.speechSynthesis.onvoiceschanged = () =>{   //is an event that fires when the list of available voices has been updated. The assigned arrow function is a callback that executes when this event occurs.
    voices = window.speechSynthesis.getVoices(); //This line retrieves the available voices using the getVoices() method and assigns them to the voices array.
    speech.voice = voices[0];  //This sets the voice property of the SpeechSynthesisUtterance object (speech) to the first voice in the voices array

    voices.forEach((voice, i) => (voiceSelect.options[i] = new Option(voice.name, i))); //This loop iterates over the voices array and populates the <select> element (voiceSelect) with options representing different voices. It creates a new Option object for each voice and assigns the voice's name as the option text and the index i as the option value.
};

voiceSelect.addEventListener("change" , () =>{

    speech.voice = voices[voiceSelect.value] //sets the voice property of the SpeechSynthesisUtterance object (speech) to the selected voice, allowing the user to choose a specific voice from the dropdown menu.

});

document.querySelector("button").addEventListener("click", () =>{    //select button and when we click
    speech.text = document.querySelector("textarea").value;             //take  value from textarea and assign to st
    window.speechSynthesis.speak(speech);                                //using speak method we listen our speech
});

        // Make GET request to the server
fetch('http://localhost:5000/hey')
            .then(response => response.json()) // Convert the response to JSON
            .then(data => {
                // Populate the textarea with the data received from the server
                document.getElementById('text_area').value = data.user_input || "No data available";
            })
            .catch(error => {
                console.error('Error fetching data:', error);
            });