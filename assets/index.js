import 'bootstrap';
import htmx from 'htmx.org/dist/htmx.esm';
import { init } from "universalviewer";
import '@videojs/html/video/player';
import '@videojs/html/video/skin';

window.htmx = htmx;

export function makeActive(ele) {
  const navLink = document.getElementById(ele);
  navLink.setAttribute('aria-current', 'page');
  navLink.classList.add('active');
}

htmx.onLoad(function(content) {
    const navTabs = content.querySelectorAll(".htmx-tab")
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
  document.location.search = query;
};


window.addEventListener("DOMContentLoaded", (evt) => {
  const submit = document.querySelectorAll(".facet-filter-panel")
  submit.forEach(d => d.addEventListener("submit", () => facetSubmit(event, d.id)));
});

window.addEventListener("DOMContentLoaded", (evt) => {
  const scrollBtn = document.querySelector('.return-to-top-btn');

  const btnVisibility = () => {
    if (window.scrollY > 400) {
      scrollBtn.style.transition = "visibility 200ms linear, opacity 200ms linear";
      scrollBtn.style.visibility = "visible";
      scrollBtn.style.opacity = 1;
    }
    else {
      scrollBtn.style.transition = "visibility 200ms linear, opacity 200ms linear";
      scrollBtn.style.visibility = "hidden";
      scrollBtn.style.opacity = 0;
    }
  };

  window.addEventListener("scroll", () => {
    btnVisibility();
  });

  scrollBtn.addEventListener("click", () => {
    window.scrollTo({
      top: 0,
      behavior: "smooth"
    });
  });
  
})

export function initUV() {
  const uvDiv = document.querySelector("#uv");
  if (uvDiv) {
    const programManifest = uvDiv.dataset.programManifest;
    const data = {
      manifest: programManifest,
      embedded: true
    };
    init("uv", data);
  }
}

export function parseDateFilter() {
  const dateButton = document.querySelector("#date-submit");
  dateButton.addEventListener("click", () => {
    const startDate = document.querySelector("#id_start").value;
    const endDate = document.querySelector("#id_end").value;
    const paramsString = window.location.search;
    const searchParams = new URLSearchParams(paramsString);
    if (startDate) {
      if (searchParams.has("start")) {
        searchParams.set("start", startDate);
      } else {
      searchParams.append("start", startDate)
      }
    }
    if (endDate) {
      if (searchParams.has("end")) {
        searchParams.set("end", endDate);
      } else {
        searchParams.append("end", endDate)
      }
    }
    window.location = "?" + searchParams.toString();
  })
}

function moreToLess() {
  const currentText = this.innerHTML
  if (currentText === "...More") {
    this.innerHTML = "...Less"
  } else {
    this.innerHTML = "...More"
  }
}

export function moreHandler() {
  const moreButtons = document.querySelectorAll('.expand-facets')
  moreButtons.forEach(function handleItem(e) {
    e.addEventListener('click', moreToLess)
  }
)}

export function applyTabNav(baseUrl) {
  // remove any active links
  const defaultTab = document.querySelectorAll(".htmx-tab>.nav-link.active")
  defaultTab.forEach((e) => {
    e.classList.remove("active");
    e.setAttribute('aria-selected', 'false');
    e.removeAttribute('aria-current');
  });
  let paramsString = window.location.search;
  const searchParams = new URLSearchParams(paramsString);
  if (searchParams.has("first_letter")) {
    searchParams.delete("first_letter");
  };
  // JavaScript scoping means we need to define this outside the block
  let selectedTab = ''
  // check if search params are empty to select tab other than first
  if (searchParams.size > 0) {
    paramsString = "?" + searchParams.toString();
    const tabTarget = "/" + baseUrl + paramsString;
    selectedTab = document.querySelector(`[hx-get="${tabTarget}"`);
  } else {
    // select first tab as default
    const firstTab = document.querySelector('.nav-tabs').firstElementChild;
    selectedTab = firstTab.querySelector('.nav-link');
  };
    selectedTab.classList.add("active");
    selectedTab.setAttribute('aria-selected', 'true');
    selectedTab.setAttribute('aria-current', 'page');
}