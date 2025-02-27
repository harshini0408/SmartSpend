document.addEventListener("DOMContentLoaded", function () {
    const dateInput = document.getElementById("selected-date");
    const expenseForm = document.getElementById("expense-form");
    const categoryForm = document.getElementById("category-form");
    const budgetForm = document.getElementById("budget-form");
    const expenseList = document.getElementById("expense-list");
    const totalDisplay = document.getElementById("total-expenses");
    const displayedDate = document.getElementById("displayed-date");
    const monthSelector = document.getElementById("month-selector");
    const yearSelector = document.getElementById("year-selector");
    const generateReportBtn = document.getElementById("generate-report");

    let selectedDate = new Date().toISOString().split("T")[0];

    if (dateInput && displayedDate) {
        dateInput.value = selectedDate;
        displayedDate.textContent = selectedDate;

        dateInput.addEventListener("change", function () {
            selectedDate = dateInput.value;
            displayedDate.textContent = selectedDate;
            fetchExpenses(selectedDate);
        });
    } else {
        console.error("Error: Date input elements missing from the DOM.");
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
                alert(data.message);
                fetchExpenses(selectedDate);
                fetchBudgetSummary(new Date(selectedDate).getMonth() + 1, new Date(selectedDate).getFullYear());
            })
            .catch(error => console.error("Error adding expense:", error));
        });
    }

    if (categoryForm) {
        categoryForm.addEventListener("submit", function (event) {
            event.preventDefault();
            const formData = new FormData(categoryForm);

            fetch("/add_category", {
                method: "POST",
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                alert(data.message);
                location.reload();
            })
            .catch(error => console.error("Error adding category:", error));
        });
    }

    if (budgetForm) {
        budgetForm.addEventListener("submit", function (event) {
            event.preventDefault();
            const formData = new FormData(budgetForm);

            fetch("/set_budget", {
                method: "POST",
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                alert(data.message);
                fetchBudgetSummary(formData.get("month"), formData.get("year"));
            })
            .catch(error => console.error("Error setting budget:", error));
        });
    }

    function fetchExpenses(date) {
        console.log(`Fetching expenses for ${date}`);

        fetch(`/get_expenses/${date}`)
            .then(response => response.json())
            .then(expenses => {
                if (expenseList) {
                    expenseList.innerHTML = "";
                    let total = 0;
                    expenses.forEach(expense => {
                        total += expense.cost;
                        const li = document.createElement("li");
                        li.innerHTML = `${expense.name} - ₹${expense.cost} <strong>(${expense.category})</strong>`;
                        expenseList.appendChild(li);
                    });
                    if (totalDisplay) totalDisplay.textContent = `Total: ₹${total}`;
                } else {
                    console.error("Error: expenseList element is missing.");
                }
            })
            .catch(error => console.error("Error fetching expenses:", error));
    }

    function fetchBudgetSummary(month, year) {
        console.log(`Fetching budget for: Month=${month}, Year=${year}`);

        fetch(`/get_budget/${month}/${year}`)
            .then(response => response.json())
            .then(data => {
                if (data.income && data.spending_percentage) {
                    updateBudgetSummary(data.income, data.spending_percentage, data.total_spending);
                }
            })
            .catch(error => console.error("Error fetching budget summary:", error));
    }

    function updateBudgetSummary(income, spendingPercentage, totalSpending) {
        const monthlyIncome = document.getElementById("monthly-income");
        const spendingLimit = document.getElementById("spending-limit");
        const totalSpendingDisplay = document.getElementById("total-spending");
        const spendingAlert = document.getElementById("spending-alert");

        if (monthlyIncome && spendingLimit && totalSpendingDisplay) {
            const limit = income * (spendingPercentage / 100);
            monthlyIncome.textContent = `₹${income.toFixed(2)}`;
            spendingLimit.textContent = `₹${limit.toFixed(2)}`;
            totalSpendingDisplay.textContent = `₹${totalSpending.toFixed(2)}`;

            if (spendingAlert) {
                spendingAlert.style.display = totalSpending > limit ? "block" : "none";
            }
        } else {
            console.error("Error: Budget summary elements missing from the DOM.");
        }
    }

    if (generateReportBtn) {
        generateReportBtn.addEventListener("click", function () {
            const selectedMonth = monthSelector?.value;
            const selectedYear = yearSelector?.value;

            if (!selectedYear) {
                alert("Please enter a valid year.");
                return;
            }

            fetch(`/monthly_report/${selectedMonth}/${selectedYear}`)
                .then(response => response.json())
                .then(data => {
                    if (Object.keys(data).length === 0) {
                        alert("No expenses found for this month.");
                        return;
                    }
                    renderChart(data);
                })
                .catch(error => console.error("Error fetching monthly report:", error));
        });
    } else {
        console.error("Error: generateReportBtn is missing from the DOM.");
    }

    function renderChart(expenseData) {
        const ctx = document.getElementById("expenseChart")?.getContext("2d");

        if (!ctx) {
            console.error("Error: Chart canvas not found.");
            return;
        }

        if (window.expenseChart && typeof window.expenseChart.destroy === 'function') {
            window.expenseChart.destroy();
        }

        window.expenseChart = new Chart(ctx, {
            type: "pie",
            data: {
                labels: Object.keys(expenseData),
                datasets: [{
                    label: "Expenses",
                    data: Object.values(expenseData),
                    backgroundColor: ["#ff6384", "#36a2eb", "#ffce56", "#4bc0c0", "#9966ff"]
                }]
            }
        });
    }

    fetchExpenses(selectedDate);
    fetchBudgetSummary(new Date(selectedDate).getMonth() + 1, new Date(selectedDate).getFullYear());
});