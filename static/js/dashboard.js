function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}
jQuery(document).ready(function($){
    $body = (window.opera) ? (document.compatMode == "CSS1Compat" ? $('html') : $('body')) : $('html,body');
    $('.modal .form-horizontal').submit(function() {
        form = $(this);
        $.ajax({
            type : 'POST',
            url : form.attr('action'),
            data : form.serialize(),
            dataType : 'json',
            cache : false,
            beforeSend : function() {
                form.find('.js-submit').attr('disabled', true);
                form.find('.loading').toggleClass('hide');
            },
            success : function(result) {
                if (result.error > 0) {
                    form.siblings('.result').html('<i class="icon-remove icon-large"></i> ' + result.msg).show();
                    form.find('.js-submit').attr('disabled', false);
                    form.find('.loading').toggleClass('hide');
                } else {
                    form.siblings('.result').html('<i class="icon-ok icon-large"></i> ' + result.msg).removeClass('alert-error').addClass('alert-success').show();
                    form.find('.js-submit').attr('disabled', false);
                    form.find('.loading').toggleClass('hide');
                    if ($('#content').attr('data-caller') == form.attr('data-target')) {
                        $('.close').click();
                        form.siblings('.result').hide();
                        $($('#content').attr('data-caller')).click();
                    } else {
                        setTimeout(function(){
                            form.find('.js-reset').click();
                            form.siblings('.result').hide();
                            $('.close').click();
                        }, 1000);
                    }
                }
            }
        });
        return false;
    });
    $(document).on('click', '.js-api', function() {
        current = $(this);
        $.ajax({
            type : 'GET',
            url : current.attr('href'),
            success : function(result) {
                $('#content').html(result).attr('data-caller', '#' + current.attr('id'));
            }
        });
        return false;
    });
    $(document).on('click', '.category .js-edit', function() {
        target = $(this).attr('data-target');
        id = $(this).attr('data-id');
        tr = $(target);
        tr.toggleClass('hide').addClass('current-edit-row');
        $('#edit-cat-title').attr('value', tr.find('.cat-title').text());
        $('#edit-cat-slug').attr('value', tr.find('.cat-slug').text());
        $('#edit-cat-desc').html(tr.find('.cat-desc').html());
        $('#form-edit-category').attr('action', '/api/category/' + id).attr('data-target', target);
        $('#edit-category-row').insertAfter(target).toggleClass('hide');
        return false;
    });
    $(document).on('click', '.js-cancel', function() {
        $('.inline-edit-row').toggleClass('hide');
        $('.current-edit-row').toggleClass('hide').removeClass('current-edit-row');
        return false;
    });
    $(document).on('submit', '.inline-edit-form', function() {
        form = $(this);
        $.ajax({
            type : 'PUT',
            url : form.attr('action'),
            data : form.serialize(),
            dataType : 'json',
            cache : false,
            beforeSend : function() {
                form.find('.js-submit').attr('disabled', true);
                form.find('.loading').toggleClass('hide');
            },
            success : function(result) {
                if (result.error) {
                    form.find('.result').html('<i class="icon-remove icon-large"></i> ' + result.msg).show();
                    form.find('.js-submit').attr('disabled', false);
                    form.find('.loading').toggleClass('hide');
                } else {
                    $($('#content').attr('data-caller')).click();
                }
            }
        });
        return false;
    });
    $(document).on('click', '.js-delete', function() {
        current = $(this);
        if (confirm('Confirm to delete it?')) {
            $.ajax({
                type : 'DELETE',
                url : current.attr('href'),
                data : '_xsrf=' + getCookie('_xsrf'),
                dataType : 'json',
                success : function(result) {
                    if (result.error) {
                        alert(result.msg);
                    } else {
                        $(current.attr('data-target')).remove();
                    }
                }
            });
        }
        return false;
    });
    $(document).on('submit', '.post-form', function() {
        form = $(this);
        $.ajax({
            type : form.attr('method'),
            url : form.attr('action'),
            data : form.serialize(),
            dataType : 'json',
            cache : false,
            beforeSend : function() {
                form.find('.js-submit').attr('disabled', true);
                form.find('.loading').toggleClass('hide');
            },
            success : function(result) {
                if (result.error) {
                    form.find('.result').html('<i class="icon-remove icon-large"></i> ' + result.msg).show();
                } else {
                    form.find('.result').html('<i class="icon-ok icon-large"></i> ' + result.msg).removeClass('alert-error').addClass('alert-success').show();
                    if (form.attr('method') == 'POST')
                        form.find('.js-reset').click();
                }
                form.find('.js-submit').attr('disabled', false);
                form.find('.loading').toggleClass('hide');
            }
        });
        return false;
    });
    $(document).on('click', '.page .js-edit', function() {
        target = $(this).attr('data-target');
        id = $(this).attr('data-id');
        tr = $(target);
        tr.toggleClass('hide').addClass('current-edit-row');
        $('#edit-page-title').attr('value', tr.find('.page-title').text());
        $('#edit-page-slug').attr('value', tr.find('.page-slug').text());
        $('#form-edit-page').attr('action', '/api/post/' + id).attr('data-target', target);
        $('#edit-page-row').insertAfter(target).toggleClass('hide');
        return false;
    });
    $(document).on('click', '.tag .js-edit', function() {
        target = $(this).attr('data-target');
        id = $(this).attr('data-id');
        tr = $(target);
        tr.toggleClass('hide').addClass('current-edit-row');
        $('#edit-tag-title').attr('value', tr.find('.tag-title').text());
        $('#edit-tag-slug').attr('value', tr.find('.tag-slug').text());
        $('#form-edit-tag').attr('action', '/api/tag/' + id).attr('data-target', target);
        $('#edit-tag-row').insertAfter(target).toggleClass('hide');
        return false;
    });
    $(document).on('click', '.link .js-edit', function() {
        target = $(this).attr('data-target');
        id = $(this).attr('data-id');
        tr = $(target);
        tr.toggleClass('hide').addClass('current-edit-row');
        $('#edit-link-title').attr('value', tr.find('.link-title').text());
        $('#edit-link-url').attr('value', tr.find('.link-url').text());
        $('#edit-link-desc').html(tr.find('.link-desc').html());
        $('#form-edit-link').attr('action', '/api/link/' + id).attr('data-target', target);
        $('#edit-link-row').insertAfter(target).toggleClass('hide');
        return false;
    });
});