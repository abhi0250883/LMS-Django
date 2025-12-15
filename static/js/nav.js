
  // dropdown toggle for desktop
  function toggleDropdown(e){
    e.preventDefault();
    const li = e.currentTarget.closest('.nav-item');
    // close other dropdowns
    document.querySelectorAll('.nav-item').forEach(i => {
      if(i !== li) i.classList.remove('show');
    });
    li.classList.toggle('show');
  }

  // click outside closes dropdown
  document.addEventListener('click', function(ev){
    if(!ev.target.closest('.nav-item')) {
      document.querySelectorAll('.nav-item').forEach(i=>i.classList.remove('show'));
    }
  });

  // mobile menu toggle
  function toggleMobile(btn){
    const menu = document.getElementById('mobileMenu');
    const open = menu.style.display === 'flex';
    menu.style.display = open ? 'none' : 'flex';
    btn.setAttribute('aria-expanded', String(!open));
  }
