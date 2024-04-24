function getAlert() {
        const alert = document.getElementById('alert');
        console.log('alert', document.getElementById('alert'))
        const timerOne = setTimeout(() => {
            alert.classList.add('go-away');
            const timerTwo = setTimeout(() => {
                alert.style.display = 'none';
                clearTimeout(timerTwo);
            }, 800);
        clearTimeout(timerOne);

      }, 10000)
        clearTimeout(timerTwo);
}

getAlert();
