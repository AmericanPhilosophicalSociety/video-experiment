import 'bootstrap';
import htmx from 'htmx.org/dist/htmx.esm';

window.htmx = htmx;

window.onload = function() {
    const navItems = document.querySelectorAll(".main-nav-item");
    navItems.forEach(d => d.addEventListener('click', selectNav))

    function selectNav(evt) {
      let currentTab = document.querySelector('[aria-current=page]');
      currentTab.classList.remove('active')
      currentTab.removeAttribute('aria-current')
      let newTab = evt.target
      newTab.setAttribute('aria-current', 'page')
      newTab.classList.add('active')
  }
}

htmx.onLoad(function(content) {
    const navTabs = content.querySelectorAll(".nav-tab-link")
    navTabs.forEach(d => d.addEventListener('click', selectTab))

    function selectTab(evt) {
      console.log("hello world!")
      let currentTab = document.querySelector('[aria-selected=true]');
      currentTab.setAttribute('aria-selected', 'false');
      currentTab.classList.remove('active');
      currentTab.removeAttribute('aria-current');
      let newTab = evt.target;
      newTab.setAttribute('aria-selected', true);
      newTab.classList.add('active')
  }
})