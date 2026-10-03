package com.example.pipeline
import scala.util.{Try, Success, Failure}
case class Event(id: Long, name: String, payload: Map[String, String], timestamp: Long)
trait Processor {
    def process(event: Event): Event
}
class EnrichProcessor(metadata: Map[String, String]) extends Processor {
    override def process(event: Event): Event = {
        event.copy(payload = event.payload ++ metadata)
    }
}
class FilterProcessor(requiredKey: String) extends Processor {
    override def process(event: Event): Event = {
        if (event.payload.contains(requiredKey)) event
        else throw new IllegalArgumentException(s"Missing key: $requiredKey")
    }
}
class Pipeline(processors: List[Processor]) {
    def run(events: List[Event]): List[Try[Event]] = {
        events.map { event =>
            Try {
                processors.foldLeft(event) { (acc, processor) =>
                    processor.process(acc)
                }
            }
        }
    }
    def runOrThrow(events: List[Event]): List[Event] = {
        run(events).map(_.get)
    }
}
object PipelineApp {
    def main(args: Array[String]): Unit = {
        val enrich = new EnrichProcessor(Map("source" -> "api", "version" -> "2"))
        val filter = new FilterProcessor("user_id")
        val pipeline = new Pipeline(List(enrich, filter))
        val events = List(
            Event(1, "login", Map("user_id" -> "1001"), System.currentTimeMillis()),
            Event(2, "logout", Map("session" -> "abc"), System.currentTimeMillis()),
            Event(3, "purchase", Map("user_id" -> "1002"), System.currentTimeMillis())
        )
        val results = pipeline.run(events)
        results.foreach {
            case Success(event) => println(s"OK: ${event.name} -> ${event.payload}")
            case Failure(ex) => println(s"FAIL: ${ex.getMessage}")
        }
        val valid = pipeline.runOrThrow(events)
        println(s"Valid count: ${valid.size}")
        val first = events.headOption
        println(first.get.id)
        val empty = List.empty[Event]
        val nothing = empty.headOption
        println(nothing.get.name)
        val total = events.map(_.id).sum
        println(s"Total: $total")
    }
}
