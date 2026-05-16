// DOM操作が可能になった後に実行されるようにする
$(document).ready(function() {
    // ソートボタンがクリックされたときの処理
    $("th.sort-button").on("click", function() {
        var sortKey = $(this).data("sort_key");
        var order = $(this).data("order"); 
        // orderの値で、マイナスを付与・削除してソート順を切り替え
        if (order === "asc") {
            sortKey = "-" + sortKey;
        } else {
            sortKey = sortKey;
        }

        location.href = userListUrl + "?sort=" + sortKey;
    });

    function initializeSortIcons() {
        // URLパラメータからソートキーを取得
        const urlParams = new URLSearchParams(window.location.search);
        const sortParam = urlParams.get('sort');
        // カンマ区切りで複数のソートキーを取得
        const sortKeys = sortParam ? sortParam.split(',') : [];

        for (const key of sortKeys) {
            const isDescending = key.startsWith('-');
            const sortKey = isDescending ? key.substring(1) : key;
            const sortButton = $(`th.sort-button[data-sort_key='${sortKey}']`);

            if (isDescending) {
                sortButton.data('order', 'desc');
                sortButton.find('i').removeClass('fa-sort-down').addClass('fa-sort-up');
            } else {
                sortButton.data('order', 'asc');
                sortButton.find('i').removeClass('fa-sort-up').addClass('fa-sort-down');
            }
        }
    }
    initializeSortIcons();
});