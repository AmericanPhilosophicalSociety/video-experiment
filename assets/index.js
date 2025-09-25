import 'bootstrap';
import htmx from 'htmx.org/dist/htmx.esm';

window.htmx = htmx;

export function makeActive(ele) {
  const navLink = document.getElementById(ele);
  navLink.setAttribute('aria-current', 'page');
  navLink.classList.add('active');
}

htmx.onLoad(function(content) {
    const navTabs = content.querySelectorAll(".nav-tab-link")
    navTabs.forEach(d => d.addEventListener('click', selectTab))

    function selectTab(evt) {
      let currentTab = document.querySelector('[aria-selected=true]');
      currentTab.setAttribute('aria-selected', 'false');
      currentTab.classList.remove('active');
      currentTab.removeAttribute('aria-current');
      let newTab = evt.target;
      newTab.setAttribute('aria-selected', true);
      newTab.classList.add('active')
  }
});

function facetSubmit(event, element) {
  console.log(element)
  event.preventDefault();
  const form = document.getElementById(element);
  const formData = new FormData(form);
  let search = new URLSearchParams(formData);
  const badKeys = [];
  for (const [key, value] of search) {
    if (value == '') {
      badKeys.push(key);
    }
  };
  badKeys.forEach((key) => search.delete(key));
  let query = search.toString()
  console.log(query)
  document.location.search = query;
};

window.addEventListener("DOMContentLoaded", (evt) => {
  const submit = document.querySelectorAll(".facet-filter-panel")
  submit.forEach(d => d.addEventListener("submit", () => facetSubmit(event, d.id)));
});