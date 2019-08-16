--
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY microarrayobservationfact
    ADD CONSTRAINT "$1" FOREIGN KEY (microarrayobservation) REFERENCES microarrayobservation(obid);


