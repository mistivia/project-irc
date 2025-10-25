const logContainer = document.getElementById('log-container');
const dateInput = document.getElementById('log-date');

const queryString = window.location.search;
const urlParams = new URLSearchParams(queryString);
let chan = urlParams.get('chan');
let year = urlParams.get('y');
let month = urlParams.get('m');
let day = urlParams.get('d');

function getDate(year, month, day) {
    try {
        year = parseInt(year, 10);
        month = parseInt(month, 10);
        day = parseInt(day, 10);
        if (isNaN(year) || isNaN(month) || isNaN(day)) {
            throw new Error("date is NaN");
        }
        return new Date(year, month - 1, day);
    } catch (e) {
        console.log(e);
        const now = new Date();
        const y = now.toLocaleString('en-US', { timeZone: 'Asia/Shanghai', year: 'numeric' }); 
        const m = now.toLocaleString('en-US', { timeZone: 'Asia/Shanghai', month: 'numeric' }); 
        const d = now.toLocaleString('en-US', { timeZone: 'Asia/Shanghai', day: 'numeric' });
        return getDate(y, m, d);
    }
}

function formatDate(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

function setDateState(date) {
    year = date.getFullYear();
    month = String(date.getMonth() + 1).padStart(2, '0');
    day = String(date.getDate()).padStart(2, '0');
    dateInput.value = formatDate(getDate(year, month, day));
    window.history.replaceState(null, '', window.location.origin + window.location.pathname +
        '?chan=' + chan +
        '&y=' + year +
        '&m=' + month +
        '&d=' + day);
}

setDateState(getDate(year, month, day));

logContainer.innerHTML = '';

function escapeHtml(unsafe) {
    if (!unsafe) return '';
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function ircAction(text) {
    const regex =
    /^(\[[^\]]+\])(\s*<)([^>]+)(>:\s*)(\u0001ACTION\s+)([^\u0001]+)(\u0001)(.*)$/gm;
    const replacement = '$1 * $3 $6$8';
    return text.replace(regex, replacement);
}			  

function linkify(text) {
    const urlRegex = /(\b(https?):\/\/[-A-Z0-9+&@#\/%?=~_|!:,.;]*[-A-Z0-9+&@#\/%=~_|])/ig;
    return text.replace(urlRegex, function(url) {
        return `<a href="${url}" target="_blank">${url}</a>`;
    });
}

function logProcess(text) {
    text = ircAction(text);
    text = escapeHtml(text);
    text = linkify(text);
    return text;
}

function loadLog() {
    let targetUrl = 'https://raye.mistivia.com/irclog/%23' + chan + '/' + year + '/' + month + '-' + day + '.txt';
    fetch(targetUrl)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP Error: ${response.status} ${response.statusText} for hash: ${urlHash}`);
            }
            return response.text();
        })
        .then(text => {
            logContainer.innerHTML = `<pre>${logProcess(text)}</pre>`;
        })
        .catch(error => {
            console.error('Fetch error:', error);
            logContainer.innerHTML = '';
        });
}

loadLog();

function onDateChange() {
    var dateInput = this;
    var dateValue = dateInput.value;

    if (dateValue && chan) {
        var dateParts = dateValue.split('-');
        var year = dateParts[0];
        var month = dateParts[1];
        var day = dateParts[2];
        let date = getDate(year, month, day);
        setDateState(date);
        loadLog();
    }
}

document.getElementById("log-date").addEventListener('change', onDateChange, false);

function changeDate(days) {
    let currentDate = getDate(year, month, day);
    const currentDay = currentDate.getDate();
    currentDate.setDate(currentDay + days);
    setDateState(currentDate);
    dateInput.dispatchEvent(new Event('change'));
}

function setPreviousDay() {
    changeDate(-1);
    window.scrollTo(0, 0);
}

function setNextDay() {
    changeDate(1);
    window.scrollTo(0, 0);
}

function setToday() {
    let date = getDate('', '', '');
    setDateState(date);
    dateInput.dispatchEvent(new Event('change'));
}