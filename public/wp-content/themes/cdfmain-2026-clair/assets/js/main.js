/**
 * CDF Clair — nav + FAQ accordion.
 */
(function () {
	function initNav() {
		var toggle = document.querySelector('[data-nav-toggle]');
		var nav = document.getElementById('clair-nav');
		if (!toggle || !nav) {
			return;
		}
		toggle.addEventListener('click', function () {
			var open = nav.classList.toggle('is-open');
			toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
			document.body.classList.toggle('clair-nav-lock', open);
		});
		nav.querySelectorAll('a').forEach(function (a) {
			a.addEventListener('click', function () {
				nav.classList.remove('is-open');
				toggle.setAttribute('aria-expanded', 'false');
				document.body.classList.remove('clair-nav-lock');
			});
		});
	}

	function initFaq() {
		var roots = document.querySelectorAll('[data-accordion]');
		for (var r = 0; r < roots.length; r++) {
			(function (root) {
				var buttons = root.querySelectorAll('.cdfm-faq__question');
				for (var i = 0; i < buttons.length; i++) {
					buttons[i].addEventListener('click', function () {
						var item = this.closest('.cdfm-faq__item');
						if (!item) {
							return;
						}
						var answer = item.querySelector('.cdfm-faq__answer');
						var willOpen = !item.classList.contains('is-open');
						var openItems = root.querySelectorAll('.cdfm-faq__item.is-open');
						for (var j = 0; j < openItems.length; j++) {
							openItems[j].classList.remove('is-open');
							var ob = openItems[j].querySelector('.cdfm-faq__question');
							var oa = openItems[j].querySelector('.cdfm-faq__answer');
							if (ob) {
								ob.setAttribute('aria-expanded', 'false');
							}
							if (oa) {
								oa.hidden = true;
							}
						}
						if (willOpen) {
							item.classList.add('is-open');
							this.setAttribute('aria-expanded', 'true');
							if (answer) {
								answer.hidden = false;
							}
						}
					});
				}
			})(roots[r]);
		}
	}

	function onReady() {
		initNav();
		initFaq();
	}

	if (document.readyState === 'loading') {
		document.addEventListener('DOMContentLoaded', onReady);
	} else {
		onReady();
	}
})();
