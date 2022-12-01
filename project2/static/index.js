document.addEventListener('DOMContentLoaded', () => {

    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    socket.on('connect', () => {

        // Notify the server user has joined
        socket.emit('joined');

        document.querySelector('#createChannel').addEventListener('click', () => {
            localStorage.removeItem('last_channel');
        });

        // Forget user's last channel when logged out
        document.querySelector('#logout').addEventListener('click', () => {
            localStorage.removeItem('last_channel');
        });

        document.querySelector('#comment').addEventListener("keydown", event =>{
            if(event == "Enter"){
                document.getElementById('send-button').click();
            }
        });

        // Send button emits a "message sent" event
        document.querySelector('#send-button').addEventListener("click", () => {
            
            // Save time in format HH:MM:SS
            let timestamp = new Date;
            timestamp = timestamp.toLocaleTimeString();

            let message = document.getElementById("comment").value;
            socket.emit('send message', message, timestamp);  
            document.getElementById("comment").value = '';
        });        

    });

    // When user joins a channel, add a message and on users connected.
    socket.on('status', data => {

        // Broadcast message of joined user.
        let row = '<' + `${data.msg}` + '>'
        document.querySelector('#chat').value += row + '\n';

        // Save user current channel on localStorage
        localStorage.setItem('last_channel', data.channel)
    });

    // When a message is announced, add it to the textarea.
    socket.on('announce message', data => {
        
        // Format message
        let row =  '- ' + '[ ' + `${data.user}` + ' ]:  ' + `${data.msg}` + `${'\n'}` + `${data.timestamp}`+ `${'\n'}`
        
        document.querySelector('#chat').value += row + '\n'
    });

});