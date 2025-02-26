document.addEventListener("DOMContentLoaded", function () {
    const dateInput = document.getElementById("selected-date");
    const expenseForm = document.getElementById("expense-form");
    const categoryForm = document.getElementById("category-form");
    const expenseList = document.getElementById("expense-list");
    const totalDisplay = document.getElementById("total-expenses");
    const displayedDate = document.getElementById("displayed-date");
    const monthSelector = document.getElementById("month-selector");
    const yearSelector = document.getElementById("year-selector");
    const generateReportBtn = document.getElementById("generate-report");

    let selectedDate = new Date().toISOString().split("T")[0]; // Default to today

    dateInput.value = selectedDate;
    displayedDate.textContent = selectedDate;

    dateInput.addEventListener("change", function () {
        selectedDate = dateInput.value;
        displayedDate.textContent = selectedDate;
        fetchExpenses(selectedDate);
    });

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
        })
        .catch(error => {
            console.error("Error adding expense:", error);
            alert("Failed to add expense. Please try again.");
        });
    });

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
            location.reload(); // Reload the page to update the category list
        })
        .catch(error => {
            console.error("Error adding category:", error);
            alert("Failed to add category. Please try again.");
        });
    });

    function fetchExpenses(date) {
        fetch(`/get_expenses/${date}`)
            .then(response => response.json())
            .then(expenses => {
                expenseList.innerHTML = "";
                let total = 0;
                expenses.forEach(expense => {
                    total += expense.cost;
                    const li = document.createElement("li");
                    li.innerHTML = `${expense.name} - ₹${expense.cost} <strong>(${expense.category})</strong>`;
                    expenseList.appendChild(li);
                });
                totalDisplay.textContent = `Total: ₹${total}`;
            })
            .catch(error => {
                console.error("Error fetching expenses:", error);
                alert("Failed to fetch expenses. Please try again.");
            });
    }

    generateReportBtn.addEventListener("click", function () {
        const selectedMonth = monthSelector.value;
        const selectedYear = yearSelector.value;
        
        if (!selectedYear) {
            alert("Please enter a valid year.");
            return;
        }

        fetch(`/monthly_report/${selectedMonth}/${selectedYear}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error("Failed to fetch monthly report.");
                }
                return response.json();
            })
            .then(data => {
                if (Object.keys(data).length === 0) {
                    alert("No expenses found for this month.");
                    return;
                }
                renderChart(data);
            })
            .catch(error => {
                console.error("Error fetching monthly report:", error);
                alert("Failed to generate monthly report. Please try again.");
            });
    });

    function renderChart(expenseData) {
        const ctx = document.getElementById("expenseChart").getContext("2d");

        // Destroy existing chart only if it exists and is a valid Chart.js instance
        if (window.expenseChart && typeof window.expenseChart.destroy === 'function') {
            window.expenseChart.destroy();
        }

        // Create a new chart
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
});