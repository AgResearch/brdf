--
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY accessfact
    ADD CONSTRAINT "$1" FOREIGN KEY (ob) REFERENCES ob(obid);


