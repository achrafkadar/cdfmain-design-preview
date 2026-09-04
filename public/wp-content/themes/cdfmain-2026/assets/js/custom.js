/**
 * CDF Main 2026 — theme safety & performance tweaks.
 */
(function () {
	function hidePreloader() {
		var loader = document.getElementById('de-loader');
		if (!loader) {
			return;
		}
		loader.style.transition = 'opacity .3s ease';
		loader.style.opacity = '0';
		setTimeout(function () {
			loader.style.display = 'none';
		}, 320);
	}

	function revealWow() {
		var boxes = document.querySelectorAll('.wow');
		for (var i = 0; i < boxes.length; i++) {
			boxes[i].style.setProperty('visibility', 'visible', 'important');
			boxes[i].style.setProperty('opacity', '1', 'important');
		}
	}

	function initFaqAccordion() {
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
							var openBtn = openItems[j].querySelector('.cdfm-faq__question');
							var openAns = openItems[j].querySelector('.cdfm-faq__answer');
							if (openBtn) {
								openBtn.setAttribute('aria-expanded', 'false');
							}
							if (openAns) {
								openAns.hidden = true;
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

	function initMobileMenu() {
		var header = document.querySelector('header');
		var btn = document.getElementById('menu-btn');
		var menu = document.getElementById('mainmenu');
		if (!header || !btn || !menu) {
			return;
		}

		function syncMobileClass() {
			if (window.innerWidth <= 992) {
				header.classList.add('header-mobile');
			} else {
				header.classList.remove('header-mobile');
				header.classList.remove('menu-open');
				btn.classList.remove('menu-open');
				header.style.height = '';
				document.body.style.overflow = '';
			}
		}

		syncMobileClass();
		window.addEventListener('resize', syncMobileClass);

		btn.addEventListener('click', function (e) {
			if (window.innerWidth > 992) {
				return;
			}
			e.preventDefault();
			e.stopPropagation();
			var open = !header.classList.contains('menu-open');
			header.classList.toggle('menu-open', open);
			btn.classList.toggle('menu-open', open);
			header.style.height = open ? window.innerHeight + 'px' : 'auto';
			document.body.style.overflow = open ? 'hidden' : '';
		}, true);

		menu.addEventListener('click', function (e) {
			var link = e.target.closest('a');
			if (!link || window.innerWidth > 992) {
				return;
			}
			var li = link.parentElement;
			if (li && li.querySelector(':scope > ul')) {
				e.preventDefault();
				li.classList.toggle('mm-open');
				return;
			}
			header.classList.remove('menu-open');
			btn.classList.remove('menu-open');
			header.style.height = 'auto';
			document.body.style.overflow = '';
		});
	}

	function onReady() {
		hidePreloader();
		revealWow();
		initFaqAccordion();
		initMobileMenu();
	}

	if (document.readyState === 'loading') {
		document.addEventListener('DOMContentLoaded', onReady);
	} else {
		onReady();
	}

	window.addEventListener('load', function () {
		hidePreloader();
		revealWow();
	});

	// on3step.js initialises WOW after load — force content visible again.
	setTimeout(revealWow, 50);
	setTimeout(revealWow, 300);
	setTimeout(revealWow, 1000);
})();
