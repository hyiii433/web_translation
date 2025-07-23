
	const dict = {
		"首页": "Home",
		"我的桌面": "My Desktop",
		"公告留言": "Announcements & Messages",
		"已收公告": "Received Announcements",
		"已收留言": "Received Messages",
		"消息通知": "Notifications",
		"个人信息": "Personal Info",
		"修改个人信息": "Edit Personal Info",
		"在线问答": "Online Q&A",
		"我的信息": "My Info",
		"教师信息查看": "Teacher Info",
		"教学周历": "Teaching Calendar",
		"教学周历查询": "Teaching Calendar Query",
		"文档管理": "Document Management",
		"文档内容管理": "Document Content Management",
		"教学服务": "Teaching Services",
		"培养方案": "Training Program",
		"专业培养方案": "Major Training Program",
		"教学计划": "Teaching Plan",
		"通选开课申请": "Elective Course Application",
		"教学任务确认": "Teaching Task Confirmation",
		"我的课表": "My Timetable",
		"个人课表信息": "Personal Timetable",
		"个人调课申请": "Personal Reschedule Application",
		"班级课表查询": "Class Timetable Query",
		"教室课表查询": "Classroom Timetable Query",
		"课程课表查询": "Course Timetable Query",
		"教学安排查询": "Teaching Arrangement Query",
		"免听/免修审核": "Exemption Review",
		"课程信息查询": "Course Info Query",
		"课程信息": "Course Info",
		"教室借用": "Classroom Borrowing",
		"教室借用申请": "Classroom Borrowing Application",
		"教室借用记录": "Classroom Borrowing Records",
		"考务成绩": "Exam & Grades",
		"考试事务": "Exam Affairs",
		"课程考试安排查询": "Course Exam Arrangement Query",
		"考务安排查询": "Exam Arrangement Query",
		"考试信息查询": "Exam Info Query",
		"监考调代申请": "Invigilation Substitute Application",
		"学生成绩": "Student Grades",
		"考勤表": "Attendance Sheet",
		"学生成绩录入": "Student Grade Entry",
		"成绩修改管理": "Grade Modification Management",
		"过程成绩管理": "Process Grade Management",
		"教学考评": "Teaching Evaluation",
		"教学评价": "Teaching Evaluation",
		"评价结果查询": "Evaluation Result Query",
		"工作量查询": "Workload Query",
		"我的评价": "My Evaluation",
		"实践实验": "Practice & Experiment",
		"毕业设计": "Graduation Project",
		"课题申报管理": "Project Application Management",
		"课题修改申请": "Project Modification Application",
		"学生选题处理": "Student Topic Handling",
		"任务书填报": "Task Book Submission",
		"开题报告查看": "Proposal Report View",
		"过程指导情况": "Process Guidance",
		"中期报告填报": "Mid-term Report Submission",
		"成绩录入": "Grade Entry",
		"教育科研": "Education & Research",
		"项目申报管理": "Project Application Management",
		"专家网上评分": "Expert Online Scoring",
		"项目查询": "Project Query",
		"项目材料模板": "Project Material Template",
		"中检专家网上评分": "Mid-term Expert Online Scoring",
		"结题专家网上评分": "Final Expert Online Scoring",
		"个人中心": "Personal Center",
		"教师": "Teacher",
		"修改密码": "Change Password",
		"退出登录": "Logout",
		"请输入菜单名": "Please enter menu name",
		"常用功能": "Common Functions",
		"教学进程": "Teaching Progress",
		"通知公告": "Announcements",
		"审核通知": "Review Notifications",
		"学生评教": "Student Evaluation",
    	"学生选课": "Student Course Selection",
    	"补考报名": "Make-up Exam Registration",
    	"重修报名": "Retake Registration",
    	"学生报到": "Student Check-in",
    	"学生注册": "Student Registration",
    	"星期一": "Monday",
    	"星期二": "Tuesday",
    	"星期三": "Wednesday",
    	"星期四": "Thursday",
    	"星期五": "Friday",
		"星期六": "Saturday",
		"星期日": "Sunday",
		"默认节次模式": "Default Session Mode",
		"查询教室借用": "Query Classroom Borrowing",
		"备注": "Remark",
		"账号": "Account",
		"密码": "Password",
		"用户登录": "User Login",
		"登录": "Login",
		"注册": "Register",
		"请输入": "Please enter",
		"忘记密码": "Forgot Password",
		"验证码": "Verification Code",
		"验证码错误": "Verification Code Error",
		"请输入验证码": "Please enter verification code"
	};

	const cnNumMap = {
		"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9, "十": 10
	};

	const enWeekMap = {
		1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five", 6: "Six", 7: "Seven", 8: "Eight", 9: "Nine", 10: "Ten",
		11: "Eleven", 12: "Twelve", 13: "Thirteen", 14: "Fourteen", 15: "Fifteen", 16: "Sixteen", 17: "Seventeen", 18: "Eighteen", 19: "Nineteen", 20: "Twenty"
	};

	function weekCnToEn(cn) {
		if (/^\d+$/.test(cn)) return enWeekMap[parseInt(cn)] || cn;
		if (cn === "十") return enWeekMap[10];
		if (cn.length === 2 && cn[0] === "十") return enWeekMap[10 + cnNumMap[cn[1]]];
		if (cn.length === 2 && cn[1] === "十") return enWeekMap[cnNumMap[cn[0]] * 10];
		if (cn.length === 2) return enWeekMap[10 + cnNumMap[cn[1]]];
		return enWeekMap[cnNumMap[cn]] || cn;
	}

	const regexDict = [
		{
			pattern: /第([一二三四五六七八九十\d]+)周/g,
			replace: (m, p1) => {
				let en = weekCnToEn(p1);
				return `Week ${en}`;
			}
		},
		{ pattern: /学年学期/g, replace: "Academic Year & Term" },
		{ pattern: /我的课程/g, replace: "My Courses" },
	];

	function injectEnglishStyle() {
    const style = document.createElement('style');
    style.innerHTML = `
        body, .edu-container, .edu-main, .edu-aside, .edu-header, .edu-sideMenu, .submenu, .edu-center, .edu-user, .edu-badge, .breadcrumbs, .personal-title, .grid__label {
            font-family: 'Segoe UI', Arial, 'Helvetica Neue', Helvetica, sans-serif !important;
            font-size: 15px !important;
            letter-spacing: 0.02em;
        }
        .edu-sideMenu .submenu li a, .edu-sideMenu .submenu li {
            font-size: 15px !important;
            white-space: nowrap !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
            line-height: 1.8 !important;
        }
        .edu-sideMenu .submenu li a b.dot {
            font-size: 12px !important;
        }
        .edu-sideMenu .link, .edu-sideMenu .submenu .link {
            font-size: 16px !important;
        }
        .edu-header .edu-user p, .edu-header .edu-user span {
            font-size: 15px !important;
        }
        .edu-sideMenu .submenu {
            min-width: 180px !important;
        }
        .edu-sideMenu .submenu li {
            position: relative !important;
            height: auto !important;
        }
        .edu-sideMenu .submenu .link {
            display: block !important;
            width: 100% !important;
        }
    `;
    document.head.appendChild(style);
}
    
	function translateTextNode(node) {
    if (node.nodeType === 3) {
        let text = node.nodeValue;
        let replaced = text;
        Object.keys(dict).sort((a, b) => b.length - a.length).forEach(zh => {
            if (replaced.includes(zh)) {
                replaced = replaced.split(zh).join(dict[zh]);
            }
        });
        regexDict.forEach(({pattern, replace}) => {
            replaced = replaced.replace(pattern, replace);
        });
        if (replaced !== text) node.nodeValue = replaced;
    }
}

	function translateAttributes(el) {
    ['placeholder', 'title', 'alt'].forEach(attr => {
        if (el.hasAttribute && el.hasAttribute(attr)) {
            let val = el.getAttribute(attr);
            if (val) {
                let replaced = val;
                Object.keys(dict).sort((a, b) => b.length - a.length).forEach(zh => {
                    if (replaced.includes(zh)) {
                        replaced = replaced.split(zh).join(dict[zh]);
                    }
                });
                regexDict.forEach(({pattern, replace}) => {
                    replaced = replaced.replace(pattern, replace);
                });
                if (replaced !== val) el.setAttribute(attr, replaced);
            }
        }
    });
}

	function walk(node) {
    translateTextNode(node);
    if (node.nodeType === 1) {
        translateAttributes(node);
        for (let child of node.childNodes) {
            walk(child);
        }
    }
}

	function translateIframes() {
    let iframes = document.querySelectorAll('iframe');
    for (let iframe of iframes) {
        try {
            let doc = iframe.contentDocument || iframe.contentWindow.document;
            if (doc && doc.body) walk(doc.body);
        } catch (e) {}
    }
}

	function observeAndTranslate() {
    walk(document.body);
    translateIframes();
}

	document.addEventListener('DOMContentLoaded', () => {
    injectEnglishStyle();
    observeAndTranslate();
});
	setInterval(observeAndTranslate, 1000);
