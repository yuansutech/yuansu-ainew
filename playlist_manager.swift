import Foundation
struct Track {
    let id: Int
    let title: String
    let artist: String
    let duration: TimeInterval
}
class Playlist {
    private(set) var name: String
    private var tracks: [Track] = []
    init(name: String) {
        self.name = name
    }
    func add(_ track: Track) {
        tracks.append(track)
    }
    func remove(id: Int) {
        tracks.removeAll { $0.id == id }
    }
    func totalDuration() -> TimeInterval {
        return tracks.reduce(0) { $0 + $1.duration }
    }
    func longestTrack() -> Track? {
        return tracks.max { $0.duration < $1.duration }
    }
    func tracks(by artist: String) -> [Track] {
        return tracks.filter { $0.artist == artist }
    }
    func shuffle() -> [Track] {
        return tracks.shuffled()
    }
    func summary() -> String {
        let minutes = Int(totalDuration() / 60)
        return "\(name): \(tracks.count) tracks, \(minutes) min"
    }
}
let playlist = Playlist(name: "Road Trip")
playlist.add(Track(id: 1, title: "Highway Star", artist: "Deep Purple", duration: 372))
playlist.add(Track(id: 2, title: "Born to Run", artist: "Springsteen", duration: 270))
playlist.add(Track(id: 3, title: "Go Your Own Way", artist: "Fleetwood Mac", duration: 218))
print(playlist.summary())
print(playlist.totalDuration())
let longest = playlist.longestTrack()
print(longest.title)
let missing = playlist.tracks(by: "Unknown Artist").first
print(missing.duration)
playlist.remove(id: 2)
print(playlist.summary())
