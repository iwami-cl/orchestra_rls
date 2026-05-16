const week = ["日", "月", "火", "水", "木", "金", "土"];
const today = new Date();
const abbreviation = "…";

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
                    // 予定がある場合、予定を最大5件まで表示
                    for (let k = 0; k < Math.min(dayOfEvents.length, 5); k++){
                        var eventElement = $(dayElement).find('.day-events').eq(k);
                        $(eventElement).text(dayOfEvents[k]["title"]);
                        $(eventElement).addClass("active");

                        // 出欠状況に応じてクラスを追加
                        let attendanceStatus = dayOfEvents[k]["my_attendance"]["status"];
                        if (attendanceStatus === 1) {
                            $(eventElement).addClass("attendance-present");
                        } else if (attendanceStatus === 2) {
                            $(eventElement).addClass("attendance-late");
                        } else if (attendanceStatus === 3) {
                            $(eventElement).addClass("attendance-leave-early");
                        } else if (attendanceStatus === 4) {
                            $(eventElement).addClass("attendance-absent");
                        } else {
                            $(eventElement).addClass("attendance-no-response");
                        }
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

    $("#add-schedule").on('click', function(){
        var addDate = new Date(showDate.getFullYear(), showDate.getMonth(), 1);
        let year = addDate.getFullYear();
        let month = addDate.getMonth() + 1; // 月は0始まりなので+1
        let day = $('#add-schedule').val();
        let dateStr = year + "-" + String(month).padStart(2, '0') + "-" + String(day).padStart(2, '0');
        let createUrl = $('#createScheduleUrl').val() + "?date=" + dateStr;
        location.href = createUrl;
    });

    $("#calendar").on('click', 'td', function() {
        // 動的に追加された要素に対しての処理

        if ($(this).parent().hasClass('header')) return;

        if ($(this).hasClass('active')){
            let val = $(this).val();
            $('#eventListForDayBody').empty();
            $("#eventListForDayHeader").text(showDate.getFullYear() + "年" + (showDate.getMonth() + 1) + "月" + val + "日の予定");
            var dayOfEvents = scheduleListMaster[val];
            if (dayOfEvents.length === 0) {
                var event_element = $(DAY_EVENT_TEMPLATE).clone();
                $(event_element).append('<div class="event-note">予定はありません</div>');
                $('#eventListForDayBody').append(event_element);
            };
            for (let i = 0; i < dayOfEvents.length; i++){
                var event_element = $(DAY_EVENT_TEMPLATE).clone();
                $(event_element).append($('<div class="event-item">' + dayOfEvents[i]["start"] + '~' + dayOfEvents[i]["end"] + '</div>'));
                
                // 予定のタイトルを表示(最大20文字)
                let title = dayOfEvents[i]["title"].substring(0, 20);
                if (dayOfEvents[i]["title"].length > 20) {
                    title += abbreviation;
                }

                $(event_element).append($('<div class="event-item">' + title + '</div>'));
                // 自分の出欠状況を表示
                let attendanceStatus = dayOfEvents[i]["my_attendance"]["status"];
                let attendanceText = "";

                if (attendanceStatus === 0) {
                    attendanceText = "未回答";
                } else if (attendanceStatus === 1) {
                    attendanceText = "出席";
                } else if (attendanceStatus === 2) {
                    attendanceText = "遅刻";
                } else if (attendanceStatus === 3) {
                    attendanceText = "早退";
                } else if (attendanceStatus === 4) {
                    attendanceText = "欠席";
                } else {
                    attendanceText = "未回答";
                }

                $(event_element).append($('<div class="event-item attendance-status">あなたの予定：' + attendanceText + '</div>'));

                // 出欠モーダルを開くボタンを追加
                let attendanceBtn = $('<button type="button" class="btn btn-sm btn-outline-primary ms-2 answer-attendance">出欠予定回答</button>');
                attendanceBtn.data('event-index', i);
                attendanceBtn.data('day', val);
                attendanceBtn.data('event-id', dayOfEvents[i]["id"]);
                $(event_element).append(attendanceBtn);

                // イベント詳細画面へのリンクボタンを追加
                let link = detailScheduleBaseUrl + dayOfEvents[i]["id"];
                let detailLink = $('<a href="' + link + '" class="btn btn-sm btn-outline-secondary ms-2">詳細</a>');
                $(event_element).append(detailLink);

                // ボタン群としてdivを追加
                let buttonGroup = $('<div class="schedule-button-group"></div>');
                buttonGroup.append(attendanceBtn);
                buttonGroup.append(detailLink);
                $(event_element).append(buttonGroup);

                $('#eventListForDayBody').append(event_element);
                $('#eventListForDayBody').append($('<hr>'));
            }

            // 出欠回答ボタンのクリックイベントを設定
            $('.answer-attendance').on('click', function(e){
                e.stopPropagation();

                // 自身のモーダルを閉じる
                eventListForDayModal.hide();

                // ここに出欠回答のモーダルを開く処理を追加
                const eventId = $(this).data('event-id');
                const eventIndex = $(this).data('event-index');
                const dayIndex = $(this).data('day');

                const events = scheduleListMaster[dayIndex];

                //eventId一致チェック処理
                if (events[eventIndex]["id"] !== eventId) {
                    console.error("Event ID mismatch");
                    return;
                }

                // モーダルにイベント情報をセット
                // 日付をフォーマット（年月日）して表示
                const eventDate = new Date(events[eventIndex]["date"]);
                const formattedDate = eventDate.getFullYear() + "年" + String(eventDate.getMonth() + 1).padStart(2, '0') + "月" + String(eventDate.getDate()).padStart(2, '0') + "日 (" + week[eventDate.getDay()] + ")";
                $('#attendanceDate').text(formattedDate);
                $('#attendanceTime').text(events[eventIndex]["start"] + " ~ " + events[eventIndex]["end"]);
                $('#attendanceTitle').text(events[eventIndex]["title"]);

                // 現在の出欠をラジオボタンに反映
                const currentAttendance = events[eventIndex]["my_attendance"]["status"];
                $(`#attendance_${currentAttendance}`).prop('checked', true);
                const attendanceNote = events[eventIndex]["my_attendance"]["note"];

                const node = $(`#attendanceNote`);
                node.val(attendanceNote);
                console.log("Selected Event ID:", eventId);
                $('#attendanceScheduleId').val(eventId);
                $('#attendanceModal').modal('show');
            });

            $("#add-schedule").val(val);
            eventListForDayModal.show();
        // } else {
        //     var addDate = new Date(showDate.getFullYear(), showDate.getMonth(), $(this).text());
        //     location.href = "http://127.0.0.1:8000/schedule/schedule/create/"
        }
    });


    $('#attendanceSubmit').on('click', function(e){
        e.stopPropagation();
        // ここに出欠回答の処理を追加
        const attendanceStatus = $('input[name="attendance"]:checked').val();
        const attendanceNote = $('#attendanceNote').val();
        const scheduleId = $('#attendanceScheduleId').val();

        const required_note = $('input[name="attendance"]:checked').attr('required_note');
        if (required_note === 'True' && attendanceNote.trim() === ''){
            alert("備考欄を入力してください。");
            return;
        }

        $.ajax({
            url: attendanceUpdateApiUrl,
            type: 'POST',
            headers: {
                'X-CSRFToken': $('#csrfToken').val()
            },
            data: {
                status: attendanceStatus,
                note: attendanceNote,
                schedule_id: scheduleId
            },
            success: function(response) {
                // 成功時の処理
                console.log(response);
                // メッセージ表示
                alert("出欠の回答を送信しました。");
                $('#attendanceModal').modal('hide');

                // カレンダーの再表示
                showProcess(showDate);
            },
            error: function(xhr, status, error) {
                // エラー時の処理
                console.error(error);
                alert("出欠の回答の送信に失敗しました。再度お試しください。");
                $('#attendanceModal').modal('hide');

                // カレンダーの再表示
                showProcess(showDate);
            }
        });
    });

    // ここに実行したい処理を書く
    showProcess(showDate)
});