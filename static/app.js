const predictionElement =
    document.getElementById("prediction");

const confidenceElement =
    document.getElementById("confidence");

const confidenceBar =
    document.getElementById("confidence-bar");

const probabilitiesElement =
    document.getElementById("probabilities");

const sequenceElement =
    document.getElementById("sequence");

const sequenceStatus =
    document.getElementById("sequence-status");

const clearButton =
    document.getElementById("clear-sequence");

const jutsuResult =
    document.getElementById("jutsu-result");

const jutsuName =
    document.getElementById("jutsu-name");

const jutsuState =
    document.getElementById("jutsu-state");


/* ==========================================
   SEQUENCE
========================================== */

let sequence = [];

let lastPrediction = null;

let predictionStartTime = 0;

let lastAddedSign = null;

const STABLE_TIME = 700;

const MAX_SEQUENCE_LENGTH = 6;


/* ==========================================
   JUTSU DATABASE
========================================== */

const JUTSUS = {

    "tiger-snake-ram": {
        name: "FIRE STYLE",
        description: "Fire Style technique detected."
    },

    "snake-horse-dragon": {
        name: "WATER STYLE",
        description: "Water Style technique detected."
    },

    "ram-tiger-bird": {
        name: "WIND STYLE",
        description: "Wind Style technique detected."
    },

    "tiger-horse-dragon": {
        name: "LIGHTNING STYLE",
        description: "Lightning Style technique detected."
    },

    "snake-ram-bird": {
        name: "EARTH STYLE",
        description: "Earth Style technique detected."
    }

};


/* ==========================================
   ICONS
========================================== */

const signIcons = {

    tiger: "🐯",

    snake: "🐍",

    horse: "🐴",

    dragon: "🐲",

    ram: "🐏",

    bird: "🐦"

};


/* ==========================================
   UPDATE AI
========================================== */

function updatePrediction(data) {

    detectedHands = 
        data.hands || [];

    const prediction =
        data.prediction;

    const confidence =
        (data.confidence || 0) * 100;


    predictionElement.textContent =
        prediction.toUpperCase();


    confidenceElement.textContent =
        confidence.toFixed(1) + "%";


    confidenceBar.style.width =
        confidence + "%";


    /* ======================================
       PROBABILITIES
    ====================================== */

    probabilitiesElement.innerHTML = "";


    const probabilities =
        data.probabilities || {};


    const sorted =
        Object.entries(
            probabilities
        ).sort(
            (a, b) => b[1] - a[1]
        );


    sorted.forEach(
        ([name, value]) => {

            const percentage =
                value * 100;


            const row =
                document.createElement(
                    "div"
                );

            row.className =
                "prob-row";


            row.innerHTML = `

                <div class="prob-header">

                    <span class="prob-name">
                        ${name.toUpperCase()}
                    </span>

                    <span class="prob-value">
                        ${percentage.toFixed(1)}%
                    </span>

                </div>

                <div class="prob-bar">

                    <div
                        class="prob-fill"
                        style="width:${percentage}%"
                    ></div>

                </div>

            `;


            probabilitiesElement.appendChild(
                row
            );

        }
    );


    /* ======================================
       SEQUENCE
    ====================================== */

    handleSequence(
        prediction,
        data.confidence || 0
    );

}


/* ==========================================
   HANDLE SEQUENCE
========================================== */

function handleSequence(
    prediction,
    confidence
) {

    const validSigns = [

        "tiger",
        "snake",
        "horse",
        "dragon",
        "ram",
        "bird"

    ];


    prediction =
        prediction.toLowerCase();


    if (
        !validSigns.includes(
            prediction
        )
    ) {

        lastPrediction = null;

        predictionStartTime = 0;

        return;
    }


    if (confidence < 0.55) {

        lastPrediction = null;

        predictionStartTime = 0;

        return;
    }


    /* ======================================
       NEW SIGN
    ====================================== */

    if (
        prediction !==
        lastPrediction
    ) {

        lastPrediction =
            prediction;

        predictionStartTime =
            Date.now();

        return;
    }


    /* ======================================
       STABLE SIGN
    ====================================== */

    const stableTime =
        Date.now() -
        predictionStartTime;


    if (
        stableTime >=
        STABLE_TIME
    ) {

        addSign(
            prediction
        );


        /*
         * Prevent the same sign from
         * being added continuously.
         */

        predictionStartTime =
            Date.now() + 100000;

    }

}


/* ==========================================
   ADD SIGN
========================================== */

function addSign(sign) {

    /* Don't add same sign twice */

    if (
        lastAddedSign === sign
    ) {
        return;
    }


    /* Maximum sequence */

    if (
        sequence.length >=
        MAX_SEQUENCE_LENGTH
    ) {
        return;
    }


    sequence.push(
        sign
    );


    lastAddedSign =
        sign;


    renderSequence();


    sequenceStatus.textContent =
        `${sequence.length} / ${MAX_SEQUENCE_LENGTH}`;


    checkForJutsu();


    console.log(
        "SEQUENCE:",
        sequence
    );

}


/* ==========================================
   RENDER SEQUENCE
========================================== */

function renderSequence() {

    sequenceElement.innerHTML = "";


    sequence.forEach(
        (sign, index) => {

            const card =
                document.createElement(
                    "div"
                );

            card.className =
                "sequence-sign";


            card.innerHTML = `

                <span class="icon">
                    ${signIcons[sign]}
                </span>

                <span class="name">
                    ${sign.toUpperCase()}
                </span>

            `;


            sequenceElement.appendChild(
                card
            );


            if (
                index <
                sequence.length - 1
            ) {

                const arrow =
                    document.createElement(
                        "div"
                    );

                arrow.className =
                    "arrow";

                arrow.textContent =
                    "→";


                sequenceElement.appendChild(
                    arrow
                );

            }

        }
    );

}


/* ==========================================
   CHECK JUTSU
========================================== */

function checkForJutsu() {

    const key =
        sequence.join("-");


    const jutsu =
        JUTSUS[key];


    if (!jutsu) {

        jutsuName.textContent =
            "UNKNOWN SEQUENCE";

        jutsuState.textContent =
            "Continue forming the hand signs.";

        jutsuResult.classList.remove(
            "activating",
            "complete"
        );

        return;
    }


    /* ======================================
       JUTSU FOUND
    ====================================== */

    jutsuName.textContent =
        jutsu.name;


    jutsuState.textContent =
        "SEQUENCE COMPLETE • ACTIVATING";


    sequenceStatus.textContent =
        "ACTIVATING";


    jutsuResult.classList.remove(
        "complete"
    );

    jutsuResult.classList.add(
        "activating"
    );


    console.log(
        "🔥 JUTSU ACTIVATED:",
        jutsu.name
    );

    if (
    jutsu.name ===
    "FIRE STYLE"
    ) {

        startFireEffect();

        startCameraFireEffect();

    }


    /* ======================================
       COMPLETE
    ====================================== */

    setTimeout(
        () => {

            jutsuResult.classList.remove(
                "activating"
            );

            jutsuResult.classList.add(
                "complete"
            );

            jutsuState.textContent =
                jutsu.description;

            sequenceStatus.textContent =
                "COMPLETE";

        },
        1200
    );

}


/* ==========================================
   CLEAR
========================================== */

clearButton.addEventListener(
    "click",
    () => {

        sequence = [];

        lastPrediction = null;

        lastAddedSign = null;

        predictionStartTime = 0;


        renderSequence();


        sequenceStatus.textContent =
            "READY";


        jutsuName.textContent =
            "AWAITING SEQUENCE";


        jutsuState.textContent =
            "Build a sequence of signs";


        jutsuResult.classList.remove(
            "activating",
            "complete"
        );

    }
);


/* ==========================================
   STATUS
========================================== */

async function updateStatus() {

    try {

        const response =
            await fetch(
                "/status?t=" +
                Date.now(),
                {
                    cache: "no-store"
                }
            );


        if (!response.ok) {

            throw new Error(
                "Server returned " +
                response.status
            );

        }


        const data =
            await response.json();


        updatePrediction(
            data
        );

    }

    catch (error) {

        console.error(
            "AI status error:",
            error
        );

    }

}


/* ==========================================
   START
========================================== */

updateStatus();

setInterval(
    updateStatus,
    150
);

/* ==========================================
   JUTSU CANVAS ENGINE
========================================== */

const canvas =
    document.getElementById("jutsu-canvas");

const ctx =
    canvas.getContext("2d");

const canvasContainer =
    document.querySelector(
        ".jutsu-canvas-container"
    );

const canvasTitle =
    document.getElementById(
        "jutsu-canvas-title"
    );


let particles = [];

let sparks = [];

let animationRunning = false;

let animationStart = 0;

let currentEffect = null;


/* ==========================================
   CANVAS SIZE
========================================== */

function resizeCanvas() {

    const rect =
        canvas.getBoundingClientRect();

    canvas.width =
        rect.width;

    canvas.height =
        rect.height;

}

window.addEventListener(
    "resize",
    resizeCanvas
);

resizeCanvas();


/* ==========================================
   RANDOM
========================================== */

function randomRange(min, max) {

    return (
        Math.random() *
        (max - min) +
        min
    );

}


/* ==========================================
   FIRE PARTICLE
========================================== */

function createFireParticle() {

    const centerX =
        canvas.width / 2;

    return {

        x:
            centerX +
            randomRange(
                -70,
                70
            ),

        y:
            canvas.height * 0.78,

        vx:
            randomRange(
                -1.5,
                1.5
            ),

        vy:
            randomRange(
                -4.5,
                -2
            ),

        size:
            randomRange(
                3,
                8
            ),

        life: 1,

        decay:
            randomRange(
                0.008,
                0.018
            ),

        wobble:
            randomRange(
                0,
                Math.PI * 2
            )

    };

}


/* ==========================================
   SPARK
========================================== */

function createSpark() {

    const angle =
        randomRange(
            0,
            Math.PI * 2
        );

    const speed =
        randomRange(
            2,
            6
        );

    return {

        x:
            canvas.width / 2,

        y:
            canvas.height * 0.72,

        vx:
            Math.cos(angle) *
            speed,

        vy:
            Math.sin(angle) *
            speed,

        life: 1,

        decay:
            randomRange(
                0.015,
                0.035
            ),

        size:
            randomRange(
                1,
                3
            )

    };

}


/* ==========================================
   SPAWN FIRE
========================================== */

function spawnFire() {

    for (
        let i = 0;
        i < 5;
        i++
    ) {

        particles.push(
            createFireParticle()
        );

    }


    for (
        let i = 0;
        i < 2;
        i++
    ) {

        sparks.push(
            createSpark()
        );

    }


    if (
        particles.length > 180
    ) {

        particles.splice(
            0,
            particles.length - 180
        );

    }


    if (
        sparks.length > 80
    ) {

        sparks.splice(
            0,
            sparks.length - 80
        );

    }

}


/* ==========================================
   DRAW BACKGROUND GLOW
========================================== */

function drawGlow(intensity) {

    const centerX =
        canvas.width / 2;

    const centerY =
        canvas.height * 0.72;


    const radius =
        canvas.height *
        0.45;


    const gradient =
        ctx.createRadialGradient(
            centerX,
            centerY,
            0,
            centerX,
            centerY,
            radius
        );


    gradient.addColorStop(
        0,
        `rgba(255,180,40,${0.28 * intensity})`
    );

    gradient.addColorStop(
        0.35,
        `rgba(255,70,10,${0.16 * intensity})`
    );

    gradient.addColorStop(
        1,
        "rgba(255,0,0,0)"
    );


    ctx.fillStyle =
        gradient;


    ctx.fillRect(
        0,
        0,
        canvas.width,
        canvas.height
    );

}


/* ==========================================
   DRAW FIREBALL
========================================== */

function drawFireball(
    scale,
    opacity
) {

    const x =
        canvas.width / 2;

    const y =
        canvas.height * 0.67;


    const radius =
        35 * scale;


    /* Outer glow */

    const glow =
        ctx.createRadialGradient(
            x,
            y,
            0,
            x,
            y,
            radius * 2.5
        );


    glow.addColorStop(
        0,
        `rgba(255,220,100,${0.75 * opacity})`
    );

    glow.addColorStop(
        0.25,
        `rgba(255,100,20,${0.45 * opacity})`
    );

    glow.addColorStop(
        1,
        "rgba(255,0,0,0)"
    );


    ctx.fillStyle =
        glow;


    ctx.beginPath();

    ctx.arc(
        x,
        y,
        radius * 2.5,
        0,
        Math.PI * 2
    );

    ctx.fill();


    /* Core */

    const core =
        ctx.createRadialGradient(
            x - radius * 0.25,
            y - radius * 0.25,
            1,
            x,
            y,
            radius
        );


    core.addColorStop(
        0,
        `rgba(255,255,220,${opacity})`
    );

    core.addColorStop(
        0.25,
        `rgba(255,220,80,${opacity})`
    );

    core.addColorStop(
        0.65,
        `rgba(255,90,10,${opacity})`
    );

    core.addColorStop(
        1,
        `rgba(150,20,0,${opacity * 0.8})`
    );


    ctx.fillStyle =
        core;


    ctx.beginPath();

    ctx.arc(
        x,
        y,
        radius,
        0,
        Math.PI * 2
    );

    ctx.fill();

}


/* ==========================================
   DRAW PARTICLES
========================================== */

function drawParticles() {

    for (
        let i = particles.length - 1;
        i >= 0;
        i--
    ) {

        const p =
            particles[i];


        p.x += p.vx;

        p.y += p.vy;

        p.vy -= 0.015;

        p.wobble += 0.08;

        p.x +=
            Math.sin(
                p.wobble
            ) * 0.4;

        p.life -=
            p.decay;


        if (
            p.life <= 0
        ) {

            particles.splice(
                i,
                1
            );

            continue;

        }


        const glow =
            ctx.createRadialGradient(
                p.x,
                p.y,
                0,
                p.x,
                p.y,
                p.size * 4
            );


        glow.addColorStop(
            0,
            `rgba(255,240,160,${p.life})`
        );

        glow.addColorStop(
            0.3,
            `rgba(255,130,30,${p.life * 0.9})`
        );

        glow.addColorStop(
            1,
            "rgba(255,20,0,0)"
        );


        ctx.fillStyle =
            glow;


        ctx.beginPath();

        ctx.arc(
            p.x,
            p.y,
            p.size * 4,
            0,
            Math.PI * 2
        );

        ctx.fill();

    }

}


/* ==========================================
   DRAW SPARKS
========================================== */

function drawSparks() {

    for (
        let i = sparks.length - 1;
        i >= 0;
        i--
    ) {

        const s =
            sparks[i];


        s.x += s.vx;

        s.y += s.vy;

        s.vy += 0.04;

        s.life -=
            s.decay;


        if (
            s.life <= 0
        ) {

            sparks.splice(
                i,
                1
            );

            continue;

        }


        ctx.globalAlpha =
            s.life;


        ctx.fillStyle =
            "rgba(255,210,100,1)";


        ctx.beginPath();

        ctx.arc(
            s.x,
            s.y,
            s.size,
            0,
            Math.PI * 2
        );

        ctx.fill();

    }


    ctx.globalAlpha = 1;

}


/* ==========================================
   FIRE ANIMATION
========================================== */

function animateFire() {

    if (
        !animationRunning
    ) {

        return;

    }


    const elapsed =
        Date.now() -
        animationStart;


    const seconds =
        elapsed / 1000;


    ctx.clearRect(
        0,
        0,
        canvas.width,
        canvas.height
    );


    /* ======================================
       PHASE 1 — CHAKRA CHARGE
       0 → 1.2 seconds
    ====================================== */

    if (
        seconds < 1.2
    ) {

        const progress =
            seconds / 1.2;


        drawGlow(
            progress
        );


        canvasTitle.textContent =
            "CHAKRA";


        const pulse =
            0.5 +
            Math.sin(
                seconds * 10
            ) * 0.2;


        drawFireball(
            0.3 + progress * 0.25,
            pulse
        );

    }


    /* ======================================
       PHASE 2 — FIRE FORMS
       1.2 → 2.8 seconds
    ====================================== */

    else if (
        seconds < 2.8
    ) {

        const progress =
            (seconds - 1.2) /
            1.6;


        drawGlow(
            1
        );


        canvasTitle.textContent =
            "FIRE STYLE";


        spawnFire();


        drawFireball(
            0.55 +
            progress * 0.7,
            1
        );


        drawParticles();

        drawSparks();

    }


    /* ======================================
       PHASE 3 — BURST
       2.8 → 4.2 seconds
    ====================================== */

    else if (
        seconds < 4.2
    ) {

        const progress =
            (seconds - 2.8) /
            1.4;


        drawGlow(
            1 -
            progress * 0.5
        );


        canvasTitle.textContent =
            "FIRE STYLE";


        spawnFire();


        const scale =
            1.25 +
            Math.sin(
                progress * Math.PI
            ) * 0.35;


        const opacity =
            1 -
            progress * 0.45;


        drawFireball(
            scale,
            opacity
        );


        drawParticles();

        drawSparks();

    }


    /* ======================================
       PHASE 4 — FADE
       4.2 → 5.5 seconds
    ====================================== */

    else if (
        seconds < 5.5
    ) {

        const progress =
            (seconds - 4.2) /
            1.3;


        const opacity =
            1 -
            progress;


        drawGlow(
            opacity
        );


        canvasTitle.textContent =
            "FIRE STYLE";


        drawFireball(
            1.6,
            opacity
        );


        drawParticles();

        drawSparks();

    }


    /* ======================================
       END
    ====================================== */

    else {

        animationRunning =
            false;

        currentEffect =
            null;

        particles = [];

        sparks = [];


        ctx.clearRect(
            0,
            0,
            canvas.width,
            canvas.height
        );


        canvasContainer.classList.remove(
            "active"
        );

        return;

    }


    requestAnimationFrame(
        animateFire
    );

}


/* ==========================================
   START FIRE STYLE
========================================== */

function startFireEffect() {

    if (
        animationRunning
    ) {

        return;

    }


    currentEffect =
        "fire";

    animationRunning =
        true;

    animationStart =
        Date.now();


    particles = [];

    sparks = [];


    canvasContainer.classList.add(
        "active"
    );


    canvasTitle.textContent =
        "CHAKRA";


    animateFire();

}

/* ==========================================
   CAMERA FIRE OVERLAY
========================================== */

const cameraCanvas =
    document.getElementById(
        "camera-jutsu-canvas"
    );

const cameraCtx =
    cameraCanvas.getContext("2d");

const cameraTitle =
    document.getElementById(
        "camera-jutsu-title"
    );

let detectedHands = [];

let cameraFireParticles = [];

let cameraFireRunning = false;

let cameraFireStart = 0;


/* ==========================================
   RESIZE
========================================== */

function resizeCameraCanvas() {

    const rect =
        cameraCanvas.getBoundingClientRect();

    cameraCanvas.width =
        rect.width;

    cameraCanvas.height =
        rect.height;

}


window.addEventListener(
    "resize",
    resizeCameraCanvas
);

resizeCameraCanvas();


/* ==========================================
   FIRE PARTICLE
========================================== */

function createCameraFireParticle() {

    let centerX =
        cameraCanvas.width / 2;

    let centerY =
        cameraCanvas.height * 0.58;

    
    if(
        detectedHands.length >= 2
    ){
        centerX =
            (detectedHands[0].x +
            detectedHands[1].x) / 2 *
            cameraCanvas.width;
        
        centerY = (
            detectedHands[0].y +
            detectedHands[1].y) / 2 *
            cameraCanvas.height

    }


    const angle =
        Math.random() *
        Math.PI * 2;


    const distance =
        Math.random() * 55;


    return {

        x:
            centerX +
            Math.cos(angle) *
            distance,

        y:
            centerY +
            Math.sin(angle) *
            distance,

        vx:
            (Math.random() - 0.5) *
            2,

        vy:
            -(Math.random() * 4 + 2),

        size:
            Math.random() * 5 + 2,

        life: 1,

        decay:
            Math.random() *
            0.02 +
            0.01

    };

}


/* ==========================================
   SPAWN
========================================== */

function spawnCameraFire() {

    for (
        let i = 0;
        i < 7;
        i++
    ) {

        cameraFireParticles.push(
            createCameraFireParticle()
        );

    }


    if (
        cameraFireParticles.length >
        180
    ) {

        cameraFireParticles.splice(
            0,
            cameraFireParticles.length -
            180
        );

    }

}


/* ==========================================
   DRAW FIREBALL
========================================== */

function drawCameraFireball(
    scale,
    opacity
) {

    let x =
        cameraCanvas.width / 2;

    let y =
        cameraCanvas.height * 0.58;
    
    if(detectedHands.length >= 2){
        x =
            (detectedHands[0].x +
            detectedHands[1].x) / 2 *
            cameraCanvas.width;
        
        y = (
            detectedHands[0].y +
            detectedHands[1].y) / 2 *
            cameraCanvas.height
    }


    const radius =
        45 * scale;


    /* Outer glow */

    const glow =
        cameraCtx.createRadialGradient(
            x,
            y,
            0,
            x,
            y,
            radius * 3
        );


    glow.addColorStop(
        0,
        `rgba(255,220,80,${0.45 * opacity})`
    );

    glow.addColorStop(
        0.35,
        `rgba(255,80,10,${0.25 * opacity})`
    );

    glow.addColorStop(
        1,
        "rgba(255,0,0,0)"
    );


    cameraCtx.fillStyle =
        glow;


    cameraCtx.beginPath();

    cameraCtx.arc(
        x,
        y,
        radius * 3,
        0,
        Math.PI * 2
    );

    cameraCtx.fill();


    /* Core */

    const core =
        cameraCtx.createRadialGradient(
            x - radius * 0.2,
            y - radius * 0.2,
            1,
            x,
            y,
            radius
        );


    core.addColorStop(
        0,
        `rgba(255,255,230,${opacity})`
    );

    core.addColorStop(
        0.25,
        `rgba(255,220,70,${opacity})`
    );

    core.addColorStop(
        0.7,
        `rgba(255,70,10,${opacity})`
    );

    core.addColorStop(
        1,
        `rgba(130,10,0,${opacity * 0.8})`
    );


    cameraCtx.fillStyle =
        core;


    cameraCtx.beginPath();

    cameraCtx.arc(
        x,
        y,
        radius,
        0,
        Math.PI * 2
    );

    cameraCtx.fill();

}


/* ==========================================
   DRAW PARTICLES
========================================== */

function drawCameraFireParticles() {

    for (
        let i =
            cameraFireParticles.length - 1;
        i >= 0;
        i--
    ) {

        const p =
            cameraFireParticles[i];


        p.x += p.vx;

        p.y += p.vy;

        p.vy -= 0.015;

        p.life -=
            p.decay;


        if (
            p.life <= 0
        ) {

            cameraFireParticles.splice(
                i,
                1
            );

            continue;

        }


        const gradient =
            cameraCtx.createRadialGradient(
                p.x,
                p.y,
                0,
                p.x,
                p.y,
                p.size * 4
            );


        gradient.addColorStop(
            0,
            `rgba(255,255,180,${p.life})`
        );

        gradient.addColorStop(
            0.3,
            `rgba(255,150,30,${p.life})`
        );

        gradient.addColorStop(
            1,
            "rgba(255,20,0,0)"
        );


        cameraCtx.fillStyle =
            gradient;


        cameraCtx.beginPath();

        cameraCtx.arc(
            p.x,
            p.y,
            p.size * 4,
            0,
            Math.PI * 2
        );

        cameraCtx.fill();

    }

}


/* ==========================================
   CAMERA FIRE ANIMATION
========================================== */

function animateCameraFire() {

    if (
        !cameraFireRunning
    ) {

        return;

    }


    const elapsed =
        Date.now() -
        cameraFireStart;


    const seconds =
        elapsed / 1000;


    cameraCtx.clearRect(
        0,
        0,
        cameraCanvas.width,
        cameraCanvas.height
    );


    /* ======================================
       CHAKRA CHARGE
    ====================================== */

    if (
        seconds < 1.2
    ) {

        const progress =
            seconds / 1.2;


        cameraTitle.textContent =
            "CHAKRA";


        drawCameraFireball(
            0.25 +
            progress * 0.25,

            0.5 +
            progress * 0.5
        );

    }


    /* ======================================
       FIRE FORMING
    ====================================== */

    else if (
        seconds < 3
    ) {

        const progress =
            (seconds - 1.2) /
            1.8;


        cameraTitle.textContent =
            "FIRE STYLE";


        spawnCameraFire();


        drawCameraFireball(
            0.5 +
            progress * 0.8,

            1
        );


        drawCameraFireParticles();

    }


    /* ======================================
       EXPLOSION
    ====================================== */

    else if (
        seconds < 4.3
    ) {

        const progress =
            (seconds - 3) /
            1.3;


        cameraTitle.textContent =
            "FIRE STYLE";


        spawnCameraFire();


        drawCameraFireball(
            1.3 +
            progress * 0.7,

            1 -
            progress * 0.5
        );


        drawCameraFireParticles();


        /* Expanding flash */

        const radius =
            progress *
            cameraCanvas.width *
            0.8;


        cameraCtx.strokeStyle =
            `rgba(255,180,60,${0.4 * (1 - progress)})`;

        cameraCtx.lineWidth =
            8;


        cameraCtx.beginPath();

        cameraCtx.arc(
            cameraCanvas.width / 2,
            cameraCanvas.height * 0.58,
            radius,
            0,
            Math.PI * 2
        );

        cameraCtx.stroke();

    }


    /* ======================================
       FADE
    ====================================== */

    else if (
        seconds < 5.5
    ) {

        const progress =
            (seconds - 4.3) /
            1.2;


        cameraTitle.textContent =
            "FIRE STYLE";


        drawCameraFireParticles();

        drawCameraFireball(
            2,

            1 - progress
        );

    }


    /* ======================================
       END
    ====================================== */

    else {

        cameraFireRunning =
            false;


        cameraFireParticles =
            [];


        cameraCtx.clearRect(
            0,
            0,
            cameraCanvas.width,
            cameraCanvas.height
        );


        cameraTitle.classList.remove(
            "active"
        );


        return;

    }


    requestAnimationFrame(
        animateCameraFire
    );

}


/* ==========================================
   START CAMERA FIRE
========================================== */

function startCameraFireEffect() {

    if (
        cameraFireRunning
    ) {

        return;

    }


    cameraFireRunning =
        true;

    cameraFireStart =
        Date.now();


    cameraFireParticles =
        [];


    cameraTitle.classList.add(
        "active"
    );


    animateCameraFire();

}