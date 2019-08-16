--
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY sequencingfact
    ADD CONSTRAINT "$1" FOREIGN KEY (sequencingfunction) REFERENCES sequencingfunction(obid);


