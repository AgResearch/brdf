--
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY urilink
    ADD CONSTRAINT "$1" FOREIGN KEY (uriob) REFERENCES uriob(obid);


