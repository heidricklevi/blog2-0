/**
 * Created by LeviJamesH on 9/5/2016.
 */

$(function () {

    $('.top-menu li').click(function () {
        $(this).addClass('active');
        $(this).siblings('li').removeClass('active');

    });
});