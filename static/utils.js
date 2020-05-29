function postAndTip(param) {
	var url = param.url;
	var csrfToken = param.csrfToken;
	var data = param.data;
	var actionName = param.actionName;
	var success = param.success;
	var fail = param.fail;
	var showSuccessTip = param.showSuccessTip;

	layui.$.ajaxSetup({
		beforeSend: function (xhr) {
			xhr.setRequestHeader("X-CSRFToken", csrfToken);
		}
	});
	layui.$.ajax({
		url: url,
		type: "POST",
		dataType: "json",
		data: data,
		async: false,
		success: function (result) {
			if (result.code === 0) {
				if (showSuccessTip) {
					layer.msg(actionName + "成功");
				}
				if (success !== undefined) {
					success(result);
				}
			} else {
				layer.msg(actionName + "失败，" + result.msg);
				if (fail !== undefined) {
					fail(result);
				}
			}
		},
		error: function (xhr) {
			console.log(xhr);
			layer.msg("请求" + actionName + "失败");
			if (fail !== undefined) {
				fail(result);
			}
		},
	});
}

function post(param) {
	var url = param.url;
	var csrfToken = param.csrfToken;
	var data = param.data;
	var actionName = param.actionName;
	var success = param.success;
	var fail = param.fail;

	layui.$.ajaxSetup({
		beforeSend: function (xhr) {
			xhr.setRequestHeader("X-CSRFToken", csrfToken);
		}
	});
	layui.$.ajax({
		url: url,
		type: "POST",
		dataType: "json",
		data: data,
		async: false,
		success: function (result) {
			if (result.code === 0) {
				if (success !== undefined) {
					success(result);
				}
			} else {
				if (fail !== undefined) {
					fail(result);
				}
			}
		},
		error: function (xhr) {
			console.log(xhr);
			if (fail !== undefined) {
				fail(result);
			}
		},
	});
}

function get(param) {
	var url = param.url;
	var success = param.success;
	var fail = param.fail;
	var data = param.data;

	layui.$.ajax({
		url: url,
		type: "GET",
		dataType: "json",
		data: data,
		async: false,
		success: function (result) {
			if (result.code === 0) {
				if (success !== undefined) {
					success(result);
				}
			} else {
				if (fail !== undefined) {
					fail(result);
				}
			}
		},
		error: function (xhr) {
			console.log(xhr);
			if (fail !== undefined) {
				fail(result);
			}
		},
	});
}

function getParam(name) {
	var reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)", "i");
	var r = window.location.search.substr(1).match(reg);
	if (r != null) return unescape(r[2]);
	return null;
}

function logout() {
	get({
		url: "/api/logout/",
		success: function (result) {
			window.location = "/";
		},
		fail: function (result) {
			layer.msg("注销失败")
		},
	})
}

function submitting() {
	layui.$(".btn-submit").addClass("layui-btn-disabled");
	layui.$(".btn-submit > i").removeClass("layui-hide");
}

function submitFailed() {
	layui.$(".btn-submit").removeClass("layui-btn-disabled");
	layui.$(".btn-submit > i").addClass("layui-hide");
}

function isSubmitting() {
	return layui.$(".btn-submit").hasClass("layui-btn-disabled");
}
