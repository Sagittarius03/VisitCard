(function($) {
    'use strict';
    
    // Функция для настройки автодополнения
    function setupAceAutocomplete() {
        // Находим все ACE редакторы
        const editors = document.querySelectorAll('.ace_editor');
        
        if (editors.length === 0) {
            // Если редактор не найден, пробуем через MutationObserver
            const observer = new MutationObserver(function(mutations) {
                const editors = document.querySelectorAll('.ace_editor');
                if (editors.length > 0) {
                    setupAceAutocomplete();
                    observer.disconnect();
                }
            });
            observer.observe(document.body, {
                childList: true,
                subtree: true
            });
            return;
        }
        
        // Настраиваем каждый редактор
        editors.forEach(function(editorElement) {
            try {
                const aceEditor = ace.edit(editorElement);
                const session = aceEditor.getSession();
                
                // Полный набор настроек автодополнения
                aceEditor.setOptions({
                    // Основные настройки автодополнения
                    enableBasicAutocompletion: true,
                    enableLiveAutocompletion: true,
                    enableSnippets: true,
                    enableEmmet: true,
                    
                    // Дополнительные настройки
                    enableMultiselect: true,
                    enableKeyboardAccessibility: true,
                    enableAutoIndent: true,
                    enableElectricChars: true,
                    
                    // Настройки отображения
                    showGutter: true,
                    displayIndentGuides: true,
                    highlightActiveLine: true,
                    highlightSelectedWord: true,
                    showInvisibles: false,
                    
                    // Настройки поведения
                    behavioursEnabled: true,
                    wrapBehavioursEnabled: true,
                });
                
                // Настраиваем автодополнение для HTML
                if (session.getMode().$id === 'ace/mode/html') {
                    // Добавляем кастомные сниппеты для HTML
                    aceEditor.setOption('enableEmmet', true);
                    
                    // Настраиваем автодополнение тегов
                    aceEditor.commands.addCommand({
                        name: 'htmlAutocomplete',
                        bindKey: { win: 'Ctrl-Space', mac: 'Ctrl-Space' },
                        exec: function(editor) {
                            editor.execCommand('startAutocomplete');
                        }
                    });
                }
                
                // Настраиваем автодополнение для JavaScript
                if (session.getMode().$id === 'ace/mode/javascript') {
                    aceEditor.setOption('enableSnippets', true);
                }
                
                // Настраиваем автодополнение для CSS
                if (session.getMode().$id === 'ace/mode/css') {
                    aceEditor.setOption('enableSnippets', true);
                }
                
                // Добавляем обработчик для автодополнения при вводе
                session.on('change', function() {
                    // Автоматическое дополнение для HTML тегов
                    if (session.getMode().$id === 'ace/mode/html') {
                        const cursor = aceEditor.getCursorPosition();
                        const line = session.getLine(cursor.row);
                        const textBefore = line.substring(0, cursor.column);
                        
                        // Если ввели открывающий тег
                        const tagMatch = textBefore.match(/<([a-zA-Z0-9]+)$/);
                        if (tagMatch) {
                            // Показываем подсказку для тега
                            const tag = tagMatch[1];
                            const completions = getHtmlCompletions(tag);
                            if (completions.length > 0) {
                                aceEditor.execCommand('startAutocomplete');
                            }
                        }
                    }
                });
                
                // Добавляем горячую клавишу для автодополнения
                aceEditor.commands.addCommand({
                    name: 'autocomplete',
                    bindKey: { win: 'Ctrl-Space', mac: 'Ctrl-Space' },
                    exec: function(editor) {
                        editor.execCommand('startAutocomplete');
                    }
                });
                
                // Добавляем горячую клавишу для сниппетов
                aceEditor.commands.addCommand({
                    name: 'snippet',
                    bindKey: { win: 'Ctrl-Enter', mac: 'Ctrl-Enter' },
                    exec: function(editor) {
                        editor.execCommand('insertSnippet');
                    }
                });
                
                console.log('✅ ACE Autocomplete настроен для:', session.getMode().$id);
                
            } catch (error) {
                console.warn('⚠️ Ошибка настройки ACE:', error);
            }
        });
    }
    
    // Функция получения подсказок для HTML тегов
    function getHtmlCompletions(tag) {
        const tags = {
            'div': ['<div></div>', '<div class=""></div>', '<div id=""></div>'],
            'span': ['<span></span>', '<span class=""></span>'],
            'p': ['<p></p>', '<p class=""></p>'],
            'h1': ['<h1></h1>'],
            'h2': ['<h2></h2>'],
            'h3': ['<h3></h3>'],
            'a': ['<a href=""></a>', '<a href="#" class=""></a>'],
            'img': ['<img src="" alt="">'],
            'ul': ['<ul><li></li></ul>'],
            'ol': ['<ol><li></li></ol>'],
            'li': ['<li></li>'],
            'table': ['<table><tr><td></td></tr></table>'],
            'tr': ['<tr><td></td></tr>'],
            'td': ['<td></td>'],
            'form': ['<form action="" method=""></form>'],
            'input': ['<input type="text" name="">', '<input type="submit" value="">'],
            'button': ['<button></button>', '<button type="submit"></button>'],
            'select': ['<select><option></option></select>'],
            'option': ['<option value=""></option>'],
            'textarea': ['<textarea name="" cols="30" rows="10"></textarea>'],
            'label': ['<label for=""></label>'],
            'section': ['<section></section>'],
            'article': ['<article></article>'],
            'header': ['<header></header>'],
            'footer': ['<footer></footer>'],
            'nav': ['<nav></nav>'],
            'main': ['<main></main>'],
            'aside': ['<aside></aside>'],
        };
        
        return tags[tag] || [];
    }
    
    // Ждем полной загрузки страницы
    $(document).ready(function() {
        // Небольшая задержка для инициализации ACE
        setTimeout(function() {
            setupAceAutocomplete();
        }, 1000);
    });
    
    // Также инициализируем при динамической загрузке
    if (document.readyState === 'complete') {
        setTimeout(function() {
            setupAceAutocomplete();
        }, 1000);
    } else {
        window.addEventListener('load', function() {
            setTimeout(function() {
                setupAceAutocomplete();
            }, 1000);
        });
    }
})(django.jQuery);