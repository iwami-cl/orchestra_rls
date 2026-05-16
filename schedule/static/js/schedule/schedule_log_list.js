const week = ["日", "月", "火", "水", "木", "金", "土"];
const today = new Date();
// 月末だとずれる可能性があるため、1日固定で取得
var showDate = new Date(today.getFullYear(), today.getMonth(), 1);
var scheduleListMaster;

const DAY_ELEMENT_TEMPLATE = '<div class="day-element"><div class="day-number"></div><div class="day-events"></div><div class="day-events"></div><div class="day-events"></div><div class="day-events"></div></div>';
const DAY_EVENT_TEMPLATE = '<div></div>';

$(function() {
    const eventListForDayModal = new bootstrap.Modal('#eventListForDayModal');

    async function getScheduleList(year, month){
        return new Promise((resolve, reject) => {
            let putUrl = $('#scheduleListApiUrl').val();
            $.ajax({
                url: putUrl + "?y=" + year + "&m=" + month,
                type: 'GET',
                dataType: 'json',
                timeout: 30000,
            })
            .done(function(data) {
                // 通信成功時の処理を記述
                resolve(data);
            })
            .fail(function() {
                // 通信失敗時の処理を記述
                reject(new Error("スケジュールの取得に失敗しました")); // 失敗 → Promiseを拒否
            });
        });
    };

    // 前の月表示
    function prev(){
        showDate.setMonth(showDate.getMonth() - 1);
        showProcess(showDate);
    }

    // 今月表示
    function now(){
        showDate = new Date(today.getFullYear(), today.getMonth(), 1);
        showProcess(showDate);
    }

    // 次の月表示
    function next(){
        showDate.setMonth(showDate.getMonth() + 1);
        showProcess(showDate);
    }

    // カレンダー表示
    async function showProcess(date) {
        var year = date.getFullYear();
        var month = date.getMonth();
        let scheduleList = await getScheduleList(year, month + 1);
        // カレンダー表示用にscheduleListを成形
        var startDayOfWeek = 1;
        var endDate = new Date(year, month + 1, 0).getDate();
        var monthScheduleList = {};
        for (var i = startDayOfWeek; i < endDate + startDayOfWeek; i++){
            monthScheduleList[i] = [];
        }

        for (let i = 0; i < scheduleList.length; i++){
            let dateStr = scheduleList[i]["date"];
            let dateObj = new Date(dateStr);
            let day = dateObj.getDate();
            monthScheduleList[day].push(scheduleList[i]);
        }

        scheduleListMaster = monthScheduleList;
        console.log(scheduleListMaster);
        document.querySelector('#monthYearDisplay').innerHTML = year + "年 " + (month + 1) + "月";

        var calendar = createProcess(year, month, scheduleListMaster);
        var $calendar = $("#calendar");
        $($calendar).empty();
        $($calendar).append($(calendar));
    }

    // カレンダー作成
    function createProcess(year, month, scheduleList) {
        var $calendar = $("<table></table>");
        // 曜日
        var $dayOfWeek = $("<tr class='dayOfWeek'></tr>");
        for (var i = 0; i < week.length; i++) {
            $($dayOfWeek).append($("<th>" + week[i] + "</th>"));
        }
        $($calendar).append($($dayOfWeek));

        var count = 0;
        var startDayOfWeek = new Date(year, month, 1).getDay();
        var endDate = new Date(year, month + 1, 0).getDate();
        var lastMonthEndDate = new Date(year, month, 0).getDate();
        var row = Math.ceil((startDayOfWeek + endDate) / week.length);

        // 1行ずつ設定
        for (var i = 0; i < row; i++) {
            $row = $("<tr>");
            // 1colum単位で設定
            for (var j = 0; j < week.length; j++) {
                // DAY_ELEMENT_TEMPLATEをディープコピー
                let dayElement = $(DAY_ELEMENT_TEMPLATE).clone();
                if (i == 0 && j < startDayOfWeek) {
                    // 1行目で1日まで先月の日付を設定
                    $(dayElement).find('.day-number').text(lastMonthEndDate - startDayOfWeek + j + 1);
                    $dayTd = $("<td class='disabled'>");
                    $($dayTd).append(dayElement);
                    $($row).append($dayTd);
                } else if (count >= endDate) {
                    // 最終行で最終日以降、翌月の日付を設定
                    count++;
                    $(dayElement).find('.day-number').text(count - endDate);
                    $dayTd = $("<td class='disabled'>");
                    $($dayTd).append(dayElement);
                    $($row).append($dayTd);
                } else {
                    // 当月の日付を曜日に照らし合わせて設定
                    count++;
                    let dayOfEvents = scheduleList[count];
                    // 活動履歴がある場合、最大5件まで表示
                    for (let k = 0; k < Math.min(dayOfEvents.length, 5); k++){
                        var eventElement = $(dayElement).find('.day-events').eq(k);
                        $(eventElement).text(dayOfEvents[k]["title"]);
                        $(eventElement).addClass("active");
                        $(eventElement).addClass("attendance-present");
                    };

                    $(dayElement).find('.day-number').text(count);
                    $dayTd = $("<td class='active'>");
                    $($dayTd).val(count);
                    $($dayTd).append(dayElement);
                    $($dayTd).append(dayElement);
                    $($row).append($dayTd);
                }
            }
            $($calendar).append($row);
        }
        return $calendar;
    }

    $("#prev").on('click', function(){
        prev();
    });

    $("#now").on('click', function(){
        now();
    });

    $("#next").on('click', function(){
        next();
    });

    $("#calendar").on('click', 'td', function() {
        // 動的に追加された要素に対しての処理

        if ($(this).parent().hasClass('header')) return;

        if ($(this).hasClass('active')){
            let val = $(this).val();
            $('#eventListForDayBody').empty();
            $("#eventListForDayHeader").text(showDate.getFullYear() + "年" + (showDate.getMonth() + 1) + "月" + val + "日の活動履歴");
            var dayOfEvents = scheduleListMaster[val];
            if (dayOfEvents.length === 0) {
                var event_element = $(DAY_EVENT_TEMPLATE).clone();
                $(event_element).append('<div class="event-note">活動履歴はありません</div>');
                $('#eventListForDayBody').append(event_element);
            };
            for (let i = 0; i < dayOfEvents.length; i++){
                var event_element = $(DAY_EVENT_TEMPLATE).clone();
                $(event_element).append($('<div class="event-item">' + dayOfEvents[i]["start"] + '~' + dayOfEvents[i]["end"] + '</div>'));
                $(event_element).append($('<div class="event-item">' + dayOfEvents[i]["title"] + '</div>'));

                // イベント詳細画面へのリンクボタンを追加
                let link = detailScheduleBaseUrl + dayOfEvents[i]["id"];
                let detailLink = $('<a href="' + link + '" class="btn btn-sm btn-outline-secondary ms-2">詳細</a>');
                $(event_element).append(detailLink);

                // ボタン群としてdivを追加
                let buttonGroup = $('<div class="schedule-button-group"></div>');
                buttonGroup.append(detailLink);
                $(event_element).append(buttonGroup);

                $('#eventListForDayBody').append(event_element);
                $('#eventListForDayBody').append($('<hr>'));
            }

            eventListForDayModal.show();
        // } else {
        //     var addDate = new Date(showDate.getFullYear(), showDate.getMonth(), $(this).text());
        //     location.href = "http://127.0.0.1:8000/schedule/schedule/create/"
        }
    });

    // ここに実行したい処理を書く
    showProcess(showDate)
});