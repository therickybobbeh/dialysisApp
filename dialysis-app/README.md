# DialysisApp

This project was generated using [Angular CLI](https://github.com/angular/angular-cli) version 19.2.2.

---

## 📖 Table of Contents
- [Philosophy](#philosophy)
- [Technologies Used](#technologies-used)
- [Development Server](#development-server)


---

## 🎯 Philosophy

### **Atomic Design Theory**
This project follows **Atomic Design Theory**, ensuring a **scalable, modular, and maintainable UI**. The UI components are structured into five layers:

1. **Atoms** – Smallest elements like buttons, inputs, labels.
2. **Molecules** – Combinations of atoms, such as form groups.
3. **Organisms** – Complex UI sections made up of molecules, such as modals or cards.
4. **Templates** – Layout structures that define the skeleton of a page.
5. **Pages** – Fully assembled UI pages using templates and organisms.

This methodology ensures **reusability**, **scalability**, and **maintainability** of UI components.

Within this we also have the following directories:
1. **Compoenets** - this will be where we store reusable components
2. **Models** - represents how data should be structured
3. **Pages** - This will be our main pages that will be rendered
4. **Services** - This will be where we store our services that will be used to fetch data from the backend and state management


---

## 🚀 Technologies Used

- **Angular** – Core framework for building the frontend.
- **PrimeNG** – Provides UI components like buttons, tables, and modals.
- **Bootstrap** – Used for responsive styling and grid layout.

---

## Environment Setup
- **Node.js** - Install Node.js from [here](https://nodejs.org/en/download/).
  - personally I use [nvm](https://github.com/nvm-sh/nvm) to manage my node versions
- **Angular CLI** - Install Angular CLI globally by running ```npm install -g @angular/cli```.

## To Run

- **Setup** - CD into this dir and run ```npm install```
- **Run Start Script** - Run ```ng start```


## Developer notes
- angular is a bit tricky to get started with. 
  - I would recommend going through the [angular docs](https://angular.io/docs) to get a better understanding of how angular works
