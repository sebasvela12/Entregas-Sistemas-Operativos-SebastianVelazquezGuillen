// Biblioteca de utilidades para demostración
var DemoLibrary = {
    // Función para calcular fibonacci de manera ineficiente (para generar más código)
    calculateFibonacci: function(n) {
        if (n <= 1) return n;
        return this.calculateFibonacci(n - 1) + this.calculateFibonacci(n - 2);
    },

    // Función para generar un array de números aleatorios
    generateRandomArray: function(size) {
        var result = [];
        for (var i = 0; i < size; i++) {
            result.push(Math.floor(Math.random() * 1000));
        }
        return result;
    },

    // Función de ordenamiento burbuja (ineficiente a propósito)
    bubbleSort: function(arr) {
        var len = arr.length;
        var temp;
        for (var i = 0; i < len; i++) {
            for (var j = 0; j < len - 1; j++) {
                if (arr[j] > arr[j + 1]) {
                    temp = arr[j];
                    arr[j] = arr[j + 1];
                    arr[j + 1] = temp;
                }
            }
        }
        return arr;
    },

    // Función para manipular el DOM
    createDynamicElements: function() {
        var container = document.createElement('div');
        container.className = 'dynamic-container';
        
        // Crear varios elementos
        for (var i = 0; i < 10; i++) {
            var element = document.createElement('div');
            element.className = 'dynamic-element';
            element.style.backgroundColor = 'rgb(' + 
                Math.floor(Math.random() * 255) + ',' + 
                Math.floor(Math.random() * 255) + ',' + 
                Math.floor(Math.random() * 255) + ')';
            element.style.width = '100px';
            element.style.height = '100px';
            element.style.margin = '10px';
            element.style.display = 'inline-block';
            element.style.transition = 'all 0.3s ease';
            
            // Añadir interactividad
            element.onmouseover = function() {
                this.style.transform = 'scale(1.1)';
                this.style.boxShadow = '0 0 10px rgba(0,0,0,0.5)';
            };
            
            element.onmouseout = function() {
                this.style.transform = 'scale(1)';
                this.style.boxShadow = 'none';
            };
            
            container.appendChild(element);
        }
        
        return container;
    },

    // Función para animar elementos
    animateElements: function() {
        var elements = document.querySelectorAll('.dynamic-element');
        for (var i = 0; i < elements.length; i++) {
            (function(index) {
                setTimeout(function() {
                    elements[index].style.transform = 'rotate(360deg)';
                    setTimeout(function() {
                        elements[index].style.transform = 'rotate(0deg)';
                    }, 1000);
                }, index * 200);
            })(i);
        }
    },

    // Función para generar texto Lorem Ipsum
    generateLoremIpsum: function() {
        var words = [
            'lorem', 'ipsum', 'dolor', 'sit', 'amet', 'consectetur',
            'adipiscing', 'elit', 'sed', 'do', 'eiusmod', 'tempor',
            'incididunt', 'ut', 'labore', 'et', 'dolore', 'magna',
            'aliqua', 'enim', 'ad', 'minim', 'veniam', 'quis',
            'nostrud', 'exercitation', 'ullamco', 'laboris', 'nisi',
            'ut', 'aliquip', 'ex', 'ea', 'commodo', 'consequat'
        ];
        
        var result = '';
        for (var i = 0; i < 100; i++) {
            result += words[Math.floor(Math.random() * words.length)] + ' ';
        }
        return result;
    },

    // Función para crear una tabla de datos
    createDataTable: function() {
        var table = document.createElement('table');
        table.className = 'data-table';
        
        // Crear encabezados
        var headers = ['ID', 'Nombre', 'Valor', 'Estado'];
        var thead = document.createElement('thead');
        var headerRow = document.createElement('tr');
        
        for (var i = 0; i < headers.length; i++) {
            var th = document.createElement('th');
            th.textContent = headers[i];
            headerRow.appendChild(th);
        }
        
        thead.appendChild(headerRow);
        table.appendChild(thead);
        
        // Crear filas de datos
        var tbody = document.createElement('tbody');
        for (var j = 0; j < 20; j++) {
            var row = document.createElement('tr');
            var id = j + 1;
            row.innerHTML = 
                '<td>' + id + '</td>' +
                '<td>Item ' + id + '</td>' +
                '<td>' + Math.floor(Math.random() * 1000) + '</td>' +
                '<td>' + (Math.random() > 0.5 ? 'Activo' : 'Inactivo') + '</td>';
            tbody.appendChild(row);
        }
        
        table.appendChild(tbody);
        return table;
    }
};

// Inicialización cuando el documento esté listo
window.onload = function() {
    console.log('Biblioteca de demostración inicializada');
    
    // Calcular algunos números de Fibonacci
    for (var i = 0; i < 20; i++) {
        console.log('Fibonacci(' + i + ') = ' + DemoLibrary.calculateFibonacci(i));
    }
    
    // Generar y ordenar un array
    var randomArray = DemoLibrary.generateRandomArray(100);
    console.log('Array ordenado:', DemoLibrary.bubbleSort(randomArray));
    
    // Crear elementos dinámicos
    document.body.appendChild(DemoLibrary.createDynamicElements());
    
    // Crear tabla de datos
    document.body.appendChild(DemoLibrary.createDataTable());
    
    // Generar texto Lorem Ipsum
    var textContainer = document.createElement('div');
    textContainer.className = 'text-container';
    textContainer.innerHTML = DemoLibrary.generateLoremIpsum();
    document.body.appendChild(textContainer);
    
    // Añadir botón para animar
    var animateButton = document.createElement('button');
    animateButton.textContent = 'Animar Elementos';
    animateButton.onclick = DemoLibrary.animateElements;
    document.body.insertBefore(animateButton, document.body.firstChild);
};