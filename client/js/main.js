// models

function Tag(id, name) {
	var self = this;

	// id does not change, so it's not observable
	self.id = id;
	self.name = ko.observable(name);
}

function Media(id, filename, path, tags) {
	var self = this;

	self.id = id;
	self.filename = filename;
	self.path = path;
	self.tags = tags;
}


// view model
function CatalogViewModel() {
	var self = this;

	// tags as received from backend; populated immediately
	self.tagList = ko.observableArray([])
	// $.getJSON('/api/tags', function(data) {
	// mock data
	var tagData = [];
	for(var i=1; i<120; i++) {
		tagData.push({'id': i, 'name': 'Tag ' + i});
	}
	
	tagData = $.map(tagData, function(data, idx) {
		return new Tag(data.id, data.name);
	});
	self.tagList = ko.observableArray(tagData);
	

	// which page/view is currently being shown
	self.curPage = ko.observable('browse');
	// the list of currently matched media
	self.mediaList = ko.observableArray();
	// heading of current page
	self.title = ko.observable('Browse');

	self.clickTag = function(tag) {
		location.hash = '/media/tag/' + tag.id;
	}
	self.clickMedia = function(media) {
		console.log('launch vlc here');
	}

	self.sammy = Sammy(function() {
		this.get('#/media/tag/:tagId', function(evt) {
			// get selected tag data
			var selTag = {}
			for(var k=0; k<self.tagList().length; k++) {
				if(self.tagList()[k].id == parseInt(evt.params['tagId'])) {
					selTag = self.tagList()[k];
					break;
				}
			}

			// change title
			self.title('Tag: ' + selTag.name());

			// mock data
			var randInt = function(min, max) {
				return Math.floor(Math.random() * (max-min) + min);
			}
			var data = [];
			var filesCt = randInt(0, 100);
			for(var i=1; i<filesCt; i++) {
				var tagsCt = randInt(0, 10);
				var selectTags = [];
				for(j=0; j< tagsCt; j++) {
					selectTags.push(self.tagList()[randInt(1, 120)]);
				}
				data.push({
					'id': i, 
					'filename': 'file_' + i + '.mpg', 
					'path': '/home/marmida/somewhere/file_' + i + '.mpg',
					'tags': selectTags,
				});
			}

			// populate mediaList
			$.each(data, function(idx, mediaData) {
				self.mediaList.push(new Media(mediaData.id, mediaData.filename, mediaData.path, mediaData.tags));
			})

			// switch display
			self.curPage('mediaList');
		});

		this.get('#/browse', function() {
			self.title('Browse');
			self.curPage('browse');
		});
	});
	self.sammy.run('#/browse');

}

document.viewmodel = new CatalogViewModel();
ko.applyBindings(document.viewmodel);