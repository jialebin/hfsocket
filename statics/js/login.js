function logon_button_fun() {
    alert('asdsad');

}

function forget_password_fun() {
        swal({
			title: "哎呀密码忘了啊",
			text: "<span style='color:#449d44'>那我也没办法了啊，等后续开发吧。<span>",
			html: true,
            type: "warning",
            showCancelButton: true,
            confirmButtonColor: "#DD6B55",
            confirmButtonText: "确定！",
            cancelButtonText: "取消！",
            closeOnConfirm: false,
            closeOnCancel: false
            },
            function(isConfirm){
            if (isConfirm) {
                swal("确定我也没办法啊",'','warning');
            } else {
                swal("取消也没办法啊",'',
            "warning");
            }
        });
}

function p_1_fun() {
        swal({
			title: "来来来，你来写！",
            showCancelButton: true,
            confirmButtonColor: "#DD6B55",
            confirmButtonText: "确定！",
            cancelButtonText: "取消！",
            closeOnConfirm: false,
            closeOnCancel: false
            },
            function(isConfirm){
            if (isConfirm) {
                swal("厉害了啊",'','warning');
            } else {
                swal("啧啧啧",'',
            "warning");
            }
        });
}