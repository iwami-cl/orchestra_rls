
// ページ読み込み後に集計を実行
$(window).on('load', function() {
    // 出欠表示の切り替え
    $('#select_attendance').on('change', async function() {
        const selectedMusicId = $(this).val();
        if (selectedMusicId === 'default') {
            // パート別表示
            let attendanceData = await getAttendanceDataForPart();
            renderAttendance(attendanceData);
        } else {
            // 曲別表示
            let attendanceData = await getAttendanceDataForMusic(selectedMusicId);
            renderAttendance(attendanceData);
        }
    });

    function renderAttendance(attendanceData) {
        $('#attendance-content').empty();  // 既存の内容をクリア
        let attendance_items = Object.entries(attendanceData.attendances);
        attendance_items.forEach(([part, value]) => {
            let accordionItem = $(`<div class="accordion-item">`);
            let accordionHeader = $(`
                <h2 class="accordion-header"></h2>`
            );

            let accordionButton = $(`
                <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapse-${part}" aria-expanded="false" aria-controls="collapse-${part}">
                    <div>
                        <p class="wrap-text">${value.instrument_name}</p>
                        <table>
                            <tbody>
                                <tr>
                                    <td><span class="attend"><i class="fa-solid fa-circle-check"></i></span>&nbsp;${value.attend[1]}</td>
                                    <td><span class="late"><i class="fa-solid fa-clock"></i></span>&nbsp;${value.attend[2]}</td>
                                    <td><span class="early"><i class="fa-solid fa-right-from-bracket"></i></span>&nbsp;${value.attend[3]}</td>
                                    <td><span class="absence"><i class="fa-solid fa-circle-xmark"></i></span>&nbsp;${value.attend[4]}</td>
                                    <td><span class="pending"><i class="fa-solid fa-circle-question"></i></span>&nbsp;${value.attend[5]}</td>
                                    <td><span class="unknown"><i class="fa-solid fa-circle-minus"></i></span>&nbsp;${value.attend[0]}</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </button>
            `);
            
            let accordionBody = $(`
                <div id="collapse-${part}" class="accordion-collapse collapse">
                    <div class="accordion-body"></div>
                </div>
            `);

            for (let user of value.users) {
                let userItem = $(`
                    <div class="row">
                        <div class="col-10 text-start">
                            <div class="row">
                                <div class="col-9">
                                    <span class="username text-start wrap-text">${user.username}</span>
                                </div>
                                <div class="col-3">
                                    ${user.status == 1 ? `<span class="answer attend">出席</span>` : ''}
                                    ${user.status == 2 ? `<span class="answer late">遅刻</span>` : ''}
                                    ${user.status == 3 ? `<span class="answer early">早退</span>` : ''}
                                    ${user.status == 4 ? `<span class="answer absence">欠席</span>` : ''}
                                    ${user.status == 5 ? `<span class="answer pending">未定</span>` : ''}
                                    ${user.status == 0 ? `<span class="answer unknown">未回答</span>` : ''}
                                </div>
                            </div>
                            <p class="wrap-text">${user.note}</p>
                        </div>
                        <div class="col-2 text-start wrap-text">
                            ${user.section}
                        </div>
                    </div>
                `);
                $(accordionBody).find('.accordion-body').append(userItem);
            };


            // 内側からDOMを構築していく

            $(accordionHeader).append(accordionButton);
            $(accordionItem).append(accordionHeader);
            $(accordionItem).append(accordionBody);
            $('#attendance-content').append(accordionItem);
        });
    }

    async function getAttendanceDataForPart() {
        return $.ajax({
            url: MUSIC_ATTENDANCE_URL,
            method: 'GET',
        });
    };

    async function getAttendanceDataForMusic(music_id) {
        return $.ajax({
            url: MUSIC_ATTENDANCE_URL + `?music_id=${music_id}`,
            method: 'GET',
        });
    };

    function init() {
        // 初期表示はパート別
        $('#select_attendance').val('default');
        $('#select_attendance').trigger('change');
    }
    init();
});