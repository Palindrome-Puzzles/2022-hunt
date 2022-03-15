$('a[data-lightbox]').each(function(index, element) {
  basename = element.href.split("/").pop().split("?")[0]
  $(element).attr("data-title", '<a href="' + element.href + '" target="_blank">' + basename + '</a>')
})
