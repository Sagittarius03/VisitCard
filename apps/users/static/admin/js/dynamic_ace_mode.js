(function($) {
    'use strict';
    
    // Функция для изменения режима ACE редактора
    function updateAceMode(moduleType) {
        const editors = document.querySelectorAll('.ace_editor');
        
        if (editors.length === 0) {
            const observer = new MutationObserver(function(mutations) {
                const editors = document.querySelectorAll('.ace_editor');
                if (editors.length > 0) {
                    updateAceMode(moduleType);
                    observer.disconnect();
                }
            });
            observer.observe(document.body, {
                childList: true,
                subtree: true
            });
            return;
        }
        
        const editorElement = editors[0];
        const aceEditor = ace.edit(editorElement);
        
        // Определяем режим
        let mode = 'html';
        let emmetEnabled = false;
        
        switch(moduleType.toLowerCase()) {
            case 'html':
                mode = 'html';
                emmetEnabled = true;
                break;
            case 'javascript':
            case 'js':
                mode = 'javascript';
                break;
            case 'css':
                mode = 'css';
                break;
            case 'scss':
                mode = 'scss';
                break;
            case 'json':
                mode = 'json';
                break;
            case 'python':
                mode = 'python';
                break;
            default:
                mode = 'html';
                emmetEnabled = true;
        }
        
        // Меняем режим
        const session = aceEditor.getSession();
        session.setMode('ace/mode/' + mode);
        
        // Настройки автодополнения
        aceEditor.setOptions({
            enableBasicAutocompletion: true,
            enableLiveAutocompletion: true,
            enableSnippets: true,
            enableEmmet: emmetEnabled,
        });
        
        // Перезапускаем настройку автодополнения
        if (typeof setupAceAutocomplete === 'function') {
            setTimeout(function() {
                setupAceAutocomplete();
            }, 100);
        }
        
        console.log('🔄 ACE mode changed to:', mode);
    }
    
    // Инициализация
    function initAceEditor() {
        const moduleTypeField = document.querySelector('#id_module_type');
        
        if (moduleTypeField) {
            setTimeout(function() {
                updateAceMode(moduleTypeField.value);
            }, 500);
            
            moduleTypeField.addEventListener('change', function() {
                updateAceMode(this.value);
            });
        }
    }
    
    $(document).ready(function() {
        initAceEditor();
    });
    
    if (document.readyState === 'complete') {
        initAceEditor();
    } else {
        window.addEventListener('load', initAceEditor);
    }
})(django.jQuery);