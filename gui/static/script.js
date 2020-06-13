
function adjust_indicator_side(forward, right) {
    if (forward) {
        front_indicator.style.opacity = '1';
        back_indicator.style.opacity = '0';
        if (right) {
            front_indicator.style.transform = 'rotate(30deg)';
            front_indicator.style.left = "50px";
        } else {
            front_indicator.style.transform = 'rotate(-30deg)';
            front_indicator.style.left = "-50px";
        }


    }
    else {
        front_indicator.style.opacity = '0';
        back_indicator.style.opacity = '1';
        if (right){
            back_indicator.style.transform = 'rotate(120deg)';
            back_indicator.style.left = "50px";
        } else {
            back_indicator.style.transform = 'rotate(-150deg)';
            back_indicator.style.left = "-50px";
        }
    }

}

function up() {
    fetch('/up');
    front_indicator.style.transform = "rotate(0deg)";
    front_indicator.style.left = "0px";
    front_indicator.style.opacity = "1";
    back_indicator.style.opacity = '0';
    isForward = true

}

function down() {
    fetch('/down');
    back_indicator.style.transform = "rotate(180deg)";
        back_indicator.style.left = "0px";
    front_indicator.style.opacity = '0';
    back_indicator.style.opacity = '1';
    isForward = false
}

function left() {
    fetch('/left');
    adjust_indicator_side(isForward, false)
}

function right() {
    fetch('/right');
    front_indicator.style.transform = "rotate(30deg)";
    front_indicator.style.left = "50px";
    front_indicator.style.opacity = "1";
    back_indicator.style.opacity = '0';
    adjust_indicator_side(isForward, true)

}

function breaks() {
    front_indicator.style.opacity = '0';
    back_indicator.style.opacity = '0';
    fetch('/breaks')

}

function checkKey(e) {

    e = e || window.event;

    if (e.keyCode == '38') {
        up();
    }
    else if (e.keyCode == '40') {
        down();
    }
    else if (e.keyCode == '37') {
       left();
    }
    else if (e.keyCode == '39') {
       right();
    }
    else if (e.keyCode == '32') {
       breaks();
    }

}

function get_seed() {
    var seed = prompt("Please enter SEED");
  if (seed != null) {
    fetch('/seed/' + seed)
  }
}
function get_pass() {
    var pass = prompt("Please enter PASSWORD");
  if (pass != null) {
    fetch('/password/' + pass)
  }
}

function main() {
    document.onkeydown = checkKey;
    var front_indicator = document.getElementById('front_indicator');
    var back_indicator = document.getElementById('back_indicator');
    var isForward = true;
    get_seed()
    get_pass()
}

main()
