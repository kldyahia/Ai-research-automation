// =========================================================
// ResearchAI Frontend
// =========================================================

const API_URL = "http://127.0.0.1:8000";

const HISTORY_KEY = "researchHistory";


// =========================================================
// Elements
// =========================================================

const topicInput =
    document.getElementById("topicInput");

const researchButton =
    document.getElementById("researchButton");

const buttonText =
    document.getElementById("buttonText");

const maxRetries =
    document.getElementById("maxRetries");

const charCount =
    document.getElementById("charCount");

const loadingCard =
    document.getElementById("loadingCard");

const loadingText =
    document.getElementById("loadingText");

const reportSection =
    document.getElementById("reportSection");

const reportContent =
    document.getElementById("reportContent");

const reportTitle =
    document.getElementById("reportTitle");

const historySection =
    document.getElementById("historySection");

const historyContainer =
    document.getElementById("historyContainer");

const apiSection =
    document.getElementById("apiSection");

const emptyState =
    document.getElementById("emptyState");

const researchCard =
    document.getElementById("researchCard");

const errorToast =
    document.getElementById("errorToast");

const errorMessage =
    document.getElementById("errorMessage");

const closeError =
    document.getElementById("closeError");

const qualityScore =
    document.getElementById("qualityScore");

const retryCount =
    document.getElementById("retryCount");

const tokensUsed =
    document.getElementById("tokensUsed");

const duration =
    document.getElementById("duration");

const statusDot =
    document.getElementById("statusDot");

const largeStatusDot =
    document.getElementById("largeStatusDot");

const apiStatusText =
    document.getElementById("apiStatusText");

const largeApiStatus =
    document.getElementById("largeApiStatus");

const connectionText =
    document.getElementById("connectionText");

const themeToggle =
    document.getElementById("themeToggle");

const topThemeToggle =
    document.getElementById("topThemeToggle");

const themeIcon =
    document.getElementById("themeIcon");

const themeText =
    document.getElementById("themeText");

const newResearch =
    document.getElementById("newResearch");

const copyButton =
    document.getElementById("copyButton");

const downloadButton =
    document.getElementById("downloadButton");

const historyNav =
    document.getElementById("historyNav");

const dashboardNav =
    document.getElementById("dashboardNav");

const apiNav =
    document.getElementById("apiNav");

const clearHistoryButton =
    document.getElementById("clearHistoryButton");


// =========================================================
// Theme
// =========================================================

function setTheme(theme) {

    document.documentElement.setAttribute(
        "data-theme",
        theme
    );

    localStorage.setItem(
        "research-theme",
        theme
    );

    if (theme === "dark") {

        themeIcon.textContent = "☀";

        themeText.textContent =
            "Light Mode";

        topThemeToggle.textContent =
            "☀";

    } else {

        themeIcon.textContent = "☾";

        themeText.textContent =
            "Dark Mode";

        topThemeToggle.textContent =
            "☾";
    }
}


const savedTheme =
    localStorage.getItem(
        "research-theme"
    ) || "dark";


setTheme(savedTheme);


function toggleTheme() {

    const current =
        document.documentElement.getAttribute(
            "data-theme"
        );

    setTheme(
        current === "dark"
            ? "light"
            : "dark"
    );
}


themeToggle.addEventListener(
    "click",
    toggleTheme
);


topThemeToggle.addEventListener(
    "click",
    toggleTheme
);


// =========================================================
// Navigation
// =========================================================

function setActiveNav(activeElement) {

    document
        .querySelectorAll(".nav-item")
        .forEach(item => {
            item.classList.remove("active");
        });

    if (activeElement) {
        activeElement.classList.add("active");
    }
}


function showDashboard() {

    setActiveNav(dashboardNav);

    historySection.classList.add(
        "hidden"
    );

    apiSection.classList.add(
        "hidden"
    );

    researchCard.classList.remove(
        "hidden"
    );

    reportSection.classList.toggle(
        "hidden",
        !window.currentReport
    );

    emptyState.classList.toggle(
        "hidden",
        Boolean(window.currentReport)
    );
}


dashboardNav.addEventListener(
    "click",
    showDashboard
);


historyNav.addEventListener(
    "click",
    () => {

        setActiveNav(historyNav);

        researchCard.classList.add(
            "hidden"
        );

        reportSection.classList.add(
            "hidden"
        );

        apiSection.classList.add(
            "hidden"
        );

        emptyState.classList.add(
            "hidden"
        );

        historySection.classList.remove(
            "hidden"
        );

        renderHistory();

        historySection.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });
    }
);


apiNav.addEventListener(
    "click",
    () => {

        setActiveNav(apiNav);

        researchCard.classList.add(
            "hidden"
        );

        reportSection.classList.add(
            "hidden"
        );

        historySection.classList.add(
            "hidden"
        );

        emptyState.classList.add(
            "hidden"
        );

        apiSection.classList.remove(
            "hidden"
        );

        checkAPI();

        apiSection.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });
    }
);


// =========================================================
// Character Counter
// =========================================================

topicInput.addEventListener(
    "input",
    () => {

        charCount.textContent =
            `${topicInput.value.length} characters`;
    }
);


// =========================================================
// API Health
// =========================================================

async function checkAPI() {

    try {

        const response =
            await fetch(
                `${API_URL}/health`
            );


        if (!response.ok) {
            throw new Error(
                "API unavailable"
            );
        }


        statusDot.style.background =
            "#10b981";

        largeStatusDot.style.background =
            "#10b981";


        apiStatusText.textContent =
            "API Online";

        largeApiStatus.textContent =
            "API Online";

        connectionText.textContent =
            "API Connected";


    } catch (error) {

        statusDot.style.background =
            "#ef4444";

        largeStatusDot.style.background =
            "#ef4444";


        apiStatusText.textContent =
            "API Offline";

        largeApiStatus.textContent =
            "API Offline";

        connectionText.textContent =
            "API Offline";
    }
}


checkAPI();


// =========================================================
// Research
// =========================================================

async function startResearch() {

    const topic =
        topicInput.value.trim();


    const retries =
        Number(
            maxRetries.value
        );


    if (!topic) {

        showError(
            "Please enter a research topic."
        );

        topicInput.focus();

        return;
    }


    showDashboard();

    setLoading(true);


    try {

        const response =
            await fetch(
                `${API_URL}/research`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json",

                        "Accept":
                            "application/json"
                    },

                    body: JSON.stringify({
                        topic: topic,

                        max_retries:
                            retries
                    })
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                getErrorMessage(data)
            );
        }


        displayResearch(data);

        saveToHistory(data);


    } catch (error) {

        showError(
            error.message ||
            "Something went wrong."
        );


    } finally {

        setLoading(false);
    }
}


// =========================================================
// Display Research
// =========================================================

function displayResearch(data) {

    window.currentReport =
        data.report || "";

    window.currentTopic =
        data.topic || "Research Report";


    emptyState.classList.add(
        "hidden"
    );


    reportSection.classList.remove(
        "hidden"
    );


    qualityScore.textContent =
        formatQuality(
            data.quality_score
        );


    retryCount.textContent =
        data.retry_count ?? "—";


    tokensUsed.textContent =
        formatNumber(
            data.tokens_used
        );


    duration.textContent =
        data.duration_seconds !== undefined
            ? `${Number(
                data.duration_seconds
              ).toFixed(2)}s`
            : "—";


    reportTitle.textContent =
        data.topic ||
        "Research Report";


    if (
        typeof marked !== "undefined"
    ) {

        reportContent.innerHTML =
            marked.parse(
                data.report || ""
            );

    } else {

        reportContent.textContent =
            data.report || "";
    }


    reportSection.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });
}


// =========================================================
// Loading
// =========================================================

function setLoading(isLoading) {

    if (isLoading) {

        loadingCard.classList.remove(
            "hidden"
        );


        researchButton.disabled =
            true;


        buttonText.textContent =
            "Researching...";


        const messages = [

            "Analyzing your research topic",

            "Running autonomous research",

            "Evaluating findings",

            "Preparing the final report"
        ];


        let index = 0;


        loadingText.textContent =
            messages[index];


        window.loadingInterval =
            setInterval(() => {

                index =
                    (index + 1) %
                    messages.length;


                loadingText.textContent =
                    messages[index];

            }, 2500);


    } else {

        loadingCard.classList.add(
            "hidden"
        );


        researchButton.disabled =
            false;


        buttonText.textContent =
            "Start Research";


        clearInterval(
            window.loadingInterval
        );
    }
}


// =========================================================
// History Storage
// =========================================================

function getHistory() {

    try {

        return JSON.parse(
            localStorage.getItem(
                HISTORY_KEY
            ) || "[]"
        );

    } catch {

        return [];
    }
}


function saveToHistory(data) {

    const history =
        getHistory();


    const historyItem = {

        id:
            Date.now(),

        topic:
            data.topic || "Untitled Research",

        report:
            data.report || "",

        quality_score:
            data.quality_score ?? 0,

        retry_count:
            data.retry_count ?? 0,

        tokens_used:
            data.tokens_used ?? 0,

        duration_seconds:
            data.duration_seconds ?? 0,

        created_at:
            new Date().toISOString()
    };


    history.unshift(
        historyItem
    );


    // Keep the latest 20 researches
    const limitedHistory =
        history.slice(0, 20);


    localStorage.setItem(
        HISTORY_KEY,
        JSON.stringify(
            limitedHistory
        )
    );
}


// =========================================================
// Render History
// =========================================================

function renderHistory() {

    const history =
        getHistory();


    if (history.length === 0) {

        historyContainer.innerHTML = `

            <div class="empty-state">

                <div class="empty-icon">
                    ◷
                </div>

                <h3>
                    No research history yet
                </h3>

                <p>
                    Your completed research reports
                    will appear here.
                </p>

            </div>

        `;

        return;
    }


    historyContainer.innerHTML =
        history
            .map(
                (item, index) => {

                    const date =
                        formatDate(
                            item.created_at
                        );


                    return `

                        <div
                            class="history-item"
                            data-index="${index}"
                        >

                            <div class="history-item-main">

                                <div class="history-icon">
                                    ✦
                                </div>


                                <div class="history-info">

                                    <h3>
                                        ${escapeHTML(
                                            item.topic
                                        )}
                                    </h3>


                                    <span>
                                        ${date}
                                    </span>

                                </div>

                            </div>


                            <div class="history-metrics">

                                <div>

                                    <small>
                                        Quality
                                    </small>

                                    <strong>
                                        ${formatQuality(
                                            item.quality_score
                                        )}
                                    </strong>

                                </div>


                                <div>

                                    <small>
                                        Retries
                                    </small>

                                    <strong>
                                        ${item.retry_count}
                                    </strong>

                                </div>


                                <div>

                                    <small>
                                        Tokens
                                    </small>

                                    <strong>
                                        ${formatNumber(
                                            item.tokens_used
                                        )}
                                    </strong>

                                </div>


                                <div>

                                    <small>
                                        Duration
                                    </small>

                                    <strong>
                                        ${Number(
                                            item.duration_seconds
                                        ).toFixed(2)}s
                                    </strong>

                                </div>

                            </div>


                            <div class="history-actions">

                                <button
                                    class="open-history"
                                    data-index="${index}"
                                >
                                    Open
                                </button>


                                <button
                                    class="delete-history"
                                    data-index="${index}"
                                >
                                    Delete
                                </button>

                            </div>

                        </div>

                    `;
                }
            )
            .join("");


    document
        .querySelectorAll(".open-history")
        .forEach(button => {

            button.addEventListener(
                "click",
                () => {

                    openHistory(
                        Number(
                            button.dataset.index
                        )
                    );
                }
            );
        });


    document
        .querySelectorAll(".delete-history")
        .forEach(button => {

            button.addEventListener(
                "click",
                () => {

                    deleteHistory(
                        Number(
                            button.dataset.index
                        )
                    );
                }
            );
        });
}


// =========================================================
// Open History Item
// =========================================================

function openHistory(index) {

    const history =
        getHistory();


    const item =
        history[index];


    if (!item) {
        return;
    }


    window.currentReport =
        item.report;


    window.currentTopic =
        item.topic;


    qualityScore.textContent =
        formatQuality(
            item.quality_score
        );


    retryCount.textContent =
        item.retry_count;


    tokensUsed.textContent =
        formatNumber(
            item.tokens_used
        );


    duration.textContent =
        `${Number(
            item.duration_seconds
        ).toFixed(2)}s`;


    reportTitle.textContent =
        item.topic;


    if (
        typeof marked !== "undefined"
    ) {

        reportContent.innerHTML =
            marked.parse(
                item.report || ""
            );

    } else {

        reportContent.textContent =
            item.report || "";
    }


    historySection.classList.add(
        "hidden"
    );


    researchCard.classList.remove(
        "hidden"
    );


    reportSection.classList.remove(
        "hidden"
    );


    emptyState.classList.add(
        "hidden"
    );


    setActiveNav(
        dashboardNav
    );


    reportSection.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });
}


// =========================================================
// Delete History
// =========================================================

function deleteHistory(index) {

    const history =
        getHistory();


    history.splice(
        index,
        1
    );


    localStorage.setItem(
        HISTORY_KEY,
        JSON.stringify(history)
    );


    renderHistory();
}


// =========================================================
// Clear History
// =========================================================

clearHistoryButton.addEventListener(
    "click",
    () => {

        const history =
            getHistory();


        if (history.length === 0) {
            return;
        }


        const confirmed =
            confirm(
                "Are you sure you want to delete all research history?"
            );


        if (!confirmed) {
            return;
        }


        localStorage.removeItem(
            HISTORY_KEY
        );


        renderHistory();
    }
);


// =========================================================
// Date Formatting
// =========================================================

function formatDate(dateString) {

    if (!dateString) {
        return "";
    }


    const date =
        new Date(
            dateString
        );


    return date.toLocaleString(
        undefined,
        {
            dateStyle: "medium",

            timeStyle: "short"
        }
    );
}


// =========================================================
// HTML Escape
// =========================================================

function escapeHTML(value) {

    const div =
        document.createElement(
            "div"
        );


    div.textContent =
        value;


    return div.innerHTML;
}


// =========================================================
// Error
// =========================================================

function showError(message) {

    errorMessage.textContent =
        message;


    errorToast.classList.remove(
        "hidden"
    );


    setTimeout(() => {

        errorToast.classList.add(
            "hidden"
        );

    }, 7000);
}


closeError.addEventListener(
    "click",
    () => {

        errorToast.classList.add(
            "hidden"
        );
    }
);


function getErrorMessage(data) {

    if (data?.detail) {

        if (
            Array.isArray(
                data.detail
            )
        ) {

            return data.detail
                .map(
                    item =>
                        item.msg ||
                        "Validation error"
                )
                .join(", ");
        }


        return data.detail;
    }


    return "Research request failed.";
}


// =========================================================
// Formatting
// =========================================================

function formatQuality(value) {

    if (
        value === undefined ||
        value === null
    ) {

        return "—";
    }


    return `${(
        Number(value) * 100
    ).toFixed(0)}%`;
}


function formatNumber(value) {

    if (
        value === undefined ||
        value === null
    ) {

        return "—";
    }


    return Number(
        value
    ).toLocaleString();
}


// =========================================================
// New Research
// =========================================================

newResearch.addEventListener(
    "click",
    () => {

        topicInput.value = "";

        charCount.textContent =
            "0 characters";


        reportSection.classList.add(
            "hidden"
        );


        historySection.classList.add(
            "hidden"
        );


        apiSection.classList.add(
            "hidden"
        );


        researchCard.classList.remove(
            "hidden"
        );


        emptyState.classList.remove(
            "hidden"
        );


        qualityScore.textContent =
            "—";

        retryCount.textContent =
            "—";

        tokensUsed.textContent =
            "—";

        duration.textContent =
            "—";


        window.currentReport =
            "";

        window.currentTopic =
            "";


        setActiveNav(
            dashboardNav
        );


        topicInput.focus();


        window.scrollTo({
            top: 0,
            behavior: "smooth"
        });
    }
);


// =========================================================
// Keyboard Shortcut
// =========================================================

topicInput.addEventListener(
    "keydown",
    event => {

        if (
            event.key === "Enter" &&
            (
                event.ctrlKey ||
                event.metaKey
            )
        ) {

            event.preventDefault();

            startResearch();
        }
    }
);


// =========================================================
// Research Button
// =========================================================

researchButton.addEventListener(
    "click",
    startResearch
);


// =========================================================
// Copy Report
// =========================================================

copyButton.addEventListener(
    "click",
    async () => {

        if (!window.currentReport) {
            return;
        }


        try {

            await navigator
                .clipboard
                .writeText(
                    window.currentReport
                );


            copyButton.textContent =
                "Copied ✓";


            setTimeout(() => {

                copyButton.textContent =
                    "Copy";

            }, 1500);


        } catch {

            showError(
                "Unable to copy report."
            );
        }
    }
);


// =========================================================
// Download Markdown
// =========================================================

downloadButton.addEventListener(
    "click",
    () => {

        if (!window.currentReport) {
            return;
        }


        const content =

`# ${window.currentTopic}

${window.currentReport}
`;


        const blob =
            new Blob(
                [content],
                {
                    type:
                        "text/markdown"
                }
            );


        const url =
            URL.createObjectURL(
                blob
            );


        const link =
            document.createElement(
                "a"
            );


        link.href =
            url;


        link.download =
            "research-report.md";


        document.body.appendChild(
            link
        );


        link.click();


        link.remove();


        URL.revokeObjectURL(
            url
        );
    }
);