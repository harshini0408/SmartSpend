document.addEventListener("DOMContentLoaded", function () {
    const dateInput = document.getElementById("selected-date");
    const expenseForm = document.getElementById("expense-form");
    const expenseList = document.getElementById("expense-list");
    const totalDisplay = document.getElementById("total-expenses");
    const displayedDate = document.getElementById("displayed-date");
    const monthSelector = document.getElementById("month-selector");
    const yearSelector = document.getElementById("year-selector");
    const generateReportBtn = document.getElementById("generate-report");
    const reportSection = document.getElementById("report-section"); // Ensure this div exists

    let selectedDate = new Date().toISOString().split("T")[0];
    let expenseChart = null; // Store chart instance

    if (!monthSelector) console.error("❌ Error: Month selector not found.");
    if (!yearSelector) console.error("❌ Error: Year selector not found.");

    if (dateInput && displayedDate) {
        dateInput.value = selectedDate;
        displayedDate.textContent = selectedDate;

        dateInput.addEventListener("change", function () {
            selectedDate = dateInput.value;
            displayedDate.textContent = selectedDate;
            fetchExpenses(selectedDate);
        });
    } else {
        console.error("❌ Error: Date input elements missing.");
    }

    if (expenseForm) {
        expenseForm.addEventListener("submit", function (event) {
            event.preventDefault();
            const formData = new FormData(expenseForm);
            formData.append("date", selectedDate);

            fetch("/add_expense", {
                method: "POST",
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert("❌ Error: " + data.error);
                } else {
                    fetchExpenses(selectedDate); // ✅ Refresh expenses after adding
                    alert("✅ " + data.message);
                }
            })
            .catch(error => console.error("❌ Error adding expense:", error));

            expenseForm.reset();
        });
    }

    function fetchExpenses(date) {
        fetch(`/get_expenses/${date}`)
            .then(response => response.json())
            .then(expenses => {
                if (expenseList) {
                    expenseList.innerHTML = ""; // ✅ Clears previous expenses before adding new ones
                    let total = 0;
                    expenses.forEach(expense => {
                        total += parseFloat(expense.cost);
                        addExpenseToList(expense.name, expense.cost, expense.category);
                    });
                    if (totalDisplay) totalDisplay.textContent = `Total: ₹${total}`;
                }
            })
            .catch(error => console.error("❌ Error fetching expenses:", error));
    }

    function addExpenseToList(name, cost, category) {
        const li = document.createElement("li");
        li.innerHTML = `${name} - ₹${cost} <strong>(${category})</strong>`;
        expenseList.appendChild(li);
    }

    if (generateReportBtn) {
        generateReportBtn.addEventListener("click", function () {
            if (!monthSelector || !yearSelector) {
                alert("❌ Please select both month and year.");
                return;
            }

            const selectedMonth = monthSelector.value;
            const selectedYear = yearSelector.value;

            if (!selectedMonth || !selectedYear) {
                alert("❌ Please select both month and year.");
                return;
            }

            fetch(`/monthly_report/${selectedMonth}/${selectedYear}`)
                .then(response => response.json())
                .then(data => {
                    if (Object.keys(data).length === 0) {
                        alert("⚠️ No expenses found for this month.");
                        return;
                    }
                    console.log("📊 Monthly Report Data:", data);

                    if (reportSection) {
                        reportSection.style.display = "block";
                        reportSection.style.maxHeight = "450px"; // Keeps it compact
                        reportSection.style.overflow = "hidden"; // Prevents unnecessary scrolling
                    } else {
                        console.error("❌ Error: Report section not found in the DOM.");
                    }

                    renderChart(data);
                })
                .catch(error => console.error("❌ Error fetching monthly report:", error));
        });
    } else {
        console.error("❌ Error: generateReportBtn is missing.");
    }

    function renderChart(expenseData) {
        const ctx = document.getElementById("expenseChart")?.getContext("2d");

        if (!ctx) {
            console.error("❌ Error: Chart canvas not found.");
            return;
        }

        // ✅ Destroy old chart only if it exists
        if (expenseChart !== null) {
            expenseChart.destroy();
        }

        // ✅ Always create a Pie Chart with fixed size
        expenseChart = new Chart(ctx, {
            type: "pie",
            data: {
                labels: Object.keys(expenseData),
                datasets: [{
                    label: "Expenses",
                    data: Object.values(expenseData),
                    backgroundColor: [
                        "#ff6384", "#36a2eb", "#ffce56", "#4bc0c0", "#9966ff",
                        "#ff9f40", "#ffcd56", "#4dc9f6", "#9966ff", "#c9cbcf"
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });

        console.log("📊 Chart Updated:", expenseData);
    }

    fetchExpenses(selectedDate);
});
