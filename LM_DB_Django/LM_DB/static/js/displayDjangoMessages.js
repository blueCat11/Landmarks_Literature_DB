function displayMessage(message, type){
    UIkit.notification({
        message: message,
        status: type,
        pos: 'bottom-center',
        timeout: 2500
    });
}
