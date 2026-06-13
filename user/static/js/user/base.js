// ブラウザ通知機能
if ("Notification" in window) {
    Notification.requestPermission().then(permission => {
        if (permission === "granted") {
        console.log("通知の許可が得られました");
        }
    })
}

let notification;

// 通知を表示する関数
function showNotification(title, until, tag) {
    if (Notification.permission === "granted") {
        notification = new Notification(title, {
            body: until,
            tag: String(tag) + until,
        requireInteraction: true,  // ユーザーの操作まで通知が残る
        });

        // 任意のタイミングで自動的に通知を閉じる例
        setTimeout(() => {
            closeNotification();
        }, 10000); // 10秒後に通知を閉じる
    }
}

// 通知を閉じる関数
function closeNotification() {
    if (notification) {
        notification.close();
        notification = null; // メモリ管理のためにクリア
    }
}


// // Service Workerの登録
// if ("serviceWorker" in navigator) {
//     navigator.serviceWorker.register("/sw.js")
//         .then(() => console.log("Service Worker registered"));
// }

