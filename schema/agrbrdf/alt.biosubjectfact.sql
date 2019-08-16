--
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biosubjectfact
    ADD CONSTRAINT "$1" FOREIGN KEY (biosubjectob) REFERENCES biosubjectob(obid);


